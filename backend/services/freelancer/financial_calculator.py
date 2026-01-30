"""RN11: Complete Financial Calculator for Brazilian Freelancers.

Calculates net value considering all costs and fees:
- Platform commission (Upwork tiered, Freelancer.com flat, etc.)
- USD→BRL currency conversion via Banco Central do Brasil API
- Spread cambial (3% typical bank markup)
- IOF tax (1.1% on international transactions)
- Bank transfer fees (1% typical)
- Brazilian income taxes (Simples Nacional, MEI, Lucro Presumido)

This calculator helps freelancers understand their actual take-home pay
after all deductions, essential for pricing decisions and financial planning.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypedDict

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Enums for Type Safety
class TaxRegime(str, Enum):
    """Brazilian tax regimes for freelancers.

    Attributes:
        SIMPLES_NACIONAL: Simplified tax regime (6% on services - Anexo III)
        MEI: Individual micro-entrepreneur (R$ 66.60/month fixed)
        LUCRO_PRESUMIDO: Presumed profit regime (~11.33% effective)
        LUCRO_REAL: Actual profit regime (variable, ~15% average)
    """

    SIMPLES_NACIONAL = "Simples_Nacional"
    MEI = "MEI"
    LUCRO_PRESUMIDO = "Lucro_Presumido"
    LUCRO_REAL = "Lucro_Real"


class Platform(str, Enum):
    """Freelance platforms with different commission structures.

    Attributes:
        UPWORK: Upwork (tiered: 20%/10%/5%)
        FREELANCER: Freelancer.com (flat 10%)
        FIVERR: Fiverr (flat 20%)
        DIRECT: Direct client (0% commission)
    """

    UPWORK = "upwork"
    FREELANCER = "freelancer"
    FIVERR = "fiverr"
    DIRECT = "direct"


# Pydantic Models for Validation
class FinancialCalculationInput(BaseModel):
    """Input parameters for financial calculation.

    Attributes:
        gross_usd: Gross project value in USD
        platform: Platform name (upwork, freelancer, etc.)
        tax_regime: Brazilian tax regime
        custom_exchange_rate: Optional custom exchange rate for simulation
    """

    gross_usd: float = Field(..., gt=0, description="Gross project value in USD")
    platform: str = Field(default="upwork", description="Platform name")
    tax_regime: str = Field(default="Simples_Nacional", description="Brazilian tax regime")
    custom_exchange_rate: Optional[float] = Field(
        None, gt=0, description="Optional custom exchange rate"
    )


class ReverseCalculationInput(BaseModel):
    """Input for reverse calculation (desired net → required gross).

    Attributes:
        desired_net_brl: Desired net amount in BRL
        platform: Platform name
        tax_regime: Brazilian tax regime
    """

    desired_net_brl: float = Field(..., gt=0, description="Desired net amount in BRL")
    platform: str = Field(default="upwork", description="Platform name")
    tax_regime: str = Field(default="Simples_Nacional", description="Brazilian tax regime")


# TypedDicts for Return Types
class FinancialBreakdown(TypedDict, total=False):
    """Complete financial breakdown of a project.

    Attributes:
        gross_usd: Original gross amount in USD
        platform: Platform name
        tax_regime: Tax regime used
        exchange_rate: USD→BRL exchange rate used
        exchange_source: Source of exchange rate (banco_central, custom)
        platform_fee_usd: Platform commission in USD
        after_platform_usd: Amount after platform commission in USD
        gross_brl: Gross amount in BRL after conversion
        spread_fee_brl: Currency spread fee in BRL
        iof_brl: IOF tax in BRL
        bank_fee_brl: Bank transfer fee in BRL
        total_conversion_costs_brl: Total conversion costs in BRL
        after_conversion_brl: Amount after conversion costs in BRL
        tax_brl: Brazilian income tax in BRL
        net_brl: Final net amount in BRL
        effective_loss_rate: Total loss percentage (0.0-1.0)
        platform_fee_percentage: Platform fee as percentage
        conversion_cost_percentage: Conversion costs as percentage
        tax_percentage: Tax as percentage
        required_gross_usd: Required gross USD (for reverse calculation)
        desired_net_brl: Desired net BRL (for reverse calculation)
        warning: Warning message if any
    """

    gross_usd: float
    platform: str
    tax_regime: str
    exchange_rate: float
    exchange_source: str
    platform_fee_usd: float
    after_platform_usd: float
    gross_brl: float
    spread_fee_brl: float
    iof_brl: float
    bank_fee_brl: float
    total_conversion_costs_brl: float
    after_conversion_brl: float
    tax_brl: float
    net_brl: float
    effective_loss_rate: float
    platform_fee_percentage: float
    conversion_cost_percentage: float
    tax_percentage: float
    required_gross_usd: Optional[float]
    desired_net_brl: Optional[float]
    warning: Optional[str]


class FreelancerFinancialCalculator:
    """
    Calculates net value for Brazilian freelancers considering all costs.

    Provides comprehensive financial calculations including:
    - Platform commissions (tiered or flat)
    - Currency conversion with real-time rates
    - All Brazilian taxes and fees
    - Reverse calculations for pricing

    This is essential for Brazilian freelancers to understand their actual
    take-home pay and make informed pricing decisions.

    Attributes:
        redis: Optional Redis client for caching exchange rates
        PLATFORM_COMMISSIONS: Commission structures for each platform
        SPREAD_RATE: Currency spread rate (3%)
        IOF_RATE: IOF tax rate (1.1%)
        BANK_FEE_RATE: Bank transfer fee rate (1%)
        TAX_RATES: Tax rates for each regime

    Examples:
        >>> calculator = FreelancerFinancialCalculator()
        >>> # Calculate net for $1000 project on Upwork
        >>> result = calculator.calculate_net_value(
        ...     gross_usd=1000.0,
        ...     platform="upwork",
        ...     tax_regime="Simples_Nacional"
        ... )
        >>> print(f"Net BRL: R$ {result['net_brl']:.2f}")
        >>> # Calculate required gross for R$ 5000 net
        >>> reverse = calculator.calculate_required_gross(
        ...     desired_net_brl=5000.0,
        ...     platform="upwork",
        ...     tax_regime="Simples_Nacional"
        ... )
        >>> print(f"Charge: ${reverse['required_gross_usd']:.2f}")
    """

    # Platform commission structures
    PLATFORM_COMMISSIONS: dict[Platform, dict[str, Any]] = {
        Platform.UPWORK: {
            "type": "tiered",
            "tiers": [
                {"limit": 500.0, "rate": 0.20},  # 20% on first $500
                {"limit": 10000.0, "rate": 0.10},  # 10% from $500 to $10,000
                {"limit": float("inf"), "rate": 0.05},  # 5% above $10,000
            ],
        },
        Platform.FREELANCER: {"type": "flat", "rate": 0.10},  # 10% flat
        Platform.FIVERR: {"type": "flat", "rate": 0.20},  # 20% flat
        Platform.DIRECT: {"type": "flat", "rate": 0.0},  # 0% (direct client)
    }

    # Conversion costs (typical rates in Brazil)
    SPREAD_RATE: float = 0.03  # 3% currency spread (bank markup)
    IOF_RATE: float = 0.011  # 1.1% IOF on international transactions
    BANK_FEE_RATE: float = 0.01  # 1% bank transfer fee

    # Brazilian tax rates
    TAX_RATES: dict[TaxRegime, float] = {
        TaxRegime.SIMPLES_NACIONAL: 0.06,  # 6% (Anexo III for services)
        TaxRegime.MEI: 66.60,  # R$ 66.60/month fixed payment
        TaxRegime.LUCRO_PRESUMIDO: 0.1133,  # ~11.33% (ISS + PIS/COFINS + IRPJ)
        TaxRegime.LUCRO_REAL: 0.15,  # Variable, ~15% average
    }

    def __init__(self, redis_client: Optional[Any] = None) -> None:
        """
        Initialize financial calculator.

        Args:
            redis_client: Optional Redis client for caching exchange rates
                         (reduces API calls to Banco Central)

        Examples:
            >>> # Without caching
            >>> calculator = FreelancerFinancialCalculator()
            >>> # With Redis caching (recommended for production)
            >>> from redis import Redis
            >>> redis_client = Redis(host='localhost', port=6379)
            >>> calculator = FreelancerFinancialCalculator(redis_client)
        """
        self.redis = redis_client

    def calculate_net_value(
        self,
        gross_usd: float,
        platform: str = "upwork",
        tax_regime: str = "Simples_Nacional",
        custom_exchange_rate: Optional[float] = None,
    ) -> FinancialBreakdown:
        """
        Calculate net value (actual amount deposited in bank account).

        Applies all deductions in sequence:
        1. Platform commission
        2. Currency conversion (USD → BRL)
        3. Conversion costs (spread, IOF, bank fees)
        4. Brazilian income taxes

        Args:
            gross_usd: Gross project value in USD
            platform: Platform name (upwork, freelancer, fiverr, direct)
            tax_regime: Brazilian tax regime (Simples_Nacional, MEI, etc.)
            custom_exchange_rate: Optional custom exchange rate for simulation

        Returns:
            Complete financial breakdown with all intermediate values

        Raises:
            ValueError: If invalid platform or tax regime
            Exception: If exchange rate fetch fails (uses fallback rate)

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> # Calculate for $1000 Upwork project with Simples Nacional
            >>> result = calculator.calculate_net_value(
            ...     gross_usd=1000.0,
            ...     platform="upwork",
            ...     tax_regime="Simples_Nacional"
            ... )
            >>> print(f"Platform fee: ${result['platform_fee_usd']:.2f}")
            >>> print(f"Conversion costs: R$ {result['total_conversion_costs_brl']:.2f}")
            >>> print(f"Taxes: R$ {result['tax_brl']:.2f}")
            >>> print(f"Net: R$ {result['net_brl']:.2f}")
            >>> # Simulate with different exchange rate
            >>> result = calculator.calculate_net_value(
            ...     gross_usd=1000.0,
            ...     platform="upwork",
            ...     tax_regime="MEI",
            ...     custom_exchange_rate=6.0
            ... )
        """
        try:
            # Validate and normalize inputs
            platform_enum = self._get_platform_enum(platform)
            tax_regime_enum = self._get_tax_regime_enum(tax_regime)

            # Step 1: Calculate platform commission
            platform_fee_usd = self._calculate_platform_commission(gross_usd, platform_enum)
            after_platform_usd = gross_usd - platform_fee_usd

            # Step 2: Get exchange rate (USD → BRL)
            if custom_exchange_rate:
                exchange_rate = custom_exchange_rate
                exchange_source = "custom"
            else:
                exchange_rate = self._get_exchange_rate("USD", "BRL")
                exchange_source = "banco_central"

            gross_brl = after_platform_usd * exchange_rate

            # Step 3: Apply conversion costs
            spread_fee_brl = gross_brl * self.SPREAD_RATE
            iof_brl = gross_brl * self.IOF_RATE
            bank_fee_brl = gross_brl * self.BANK_FEE_RATE

            total_conversion_costs_brl = spread_fee_brl + iof_brl + bank_fee_brl
            after_conversion_brl = gross_brl - total_conversion_costs_brl

            # Step 4: Calculate Brazilian taxes
            tax_brl = self._calculate_taxes(after_conversion_brl, tax_regime_enum)
            net_brl = after_conversion_brl - tax_brl

            # Step 5: Calculate metrics
            total_gross_brl = gross_usd * exchange_rate
            effective_loss_rate = (
                (total_gross_brl - net_brl) / total_gross_brl if total_gross_brl > 0 else 0
            )

            return FinancialBreakdown(
                # Input parameters
                gross_usd=round(gross_usd, 2),
                platform=platform,
                tax_regime=tax_regime,
                # Exchange rate
                exchange_rate=round(exchange_rate, 4),
                exchange_source=exchange_source,
                # Platform costs
                platform_fee_usd=round(platform_fee_usd, 2),
                after_platform_usd=round(after_platform_usd, 2),
                # Conversion
                gross_brl=round(gross_brl, 2),
                spread_fee_brl=round(spread_fee_brl, 2),
                iof_brl=round(iof_brl, 2),
                bank_fee_brl=round(bank_fee_brl, 2),
                total_conversion_costs_brl=round(total_conversion_costs_brl, 2),
                after_conversion_brl=round(after_conversion_brl, 2),
                # Taxes
                tax_brl=round(tax_brl, 2),
                # Final amount
                net_brl=round(net_brl, 2),
                # Metrics (as percentages)
                effective_loss_rate=round(effective_loss_rate, 4),
                platform_fee_percentage=round(
                    (platform_fee_usd / gross_usd * 100) if gross_usd > 0 else 0, 2
                ),
                conversion_cost_percentage=round(
                    (total_conversion_costs_brl / gross_brl * 100) if gross_brl > 0 else 0, 2
                ),
                tax_percentage=round(
                    (tax_brl / after_conversion_brl * 100) if after_conversion_brl > 0 else 0,
                    2,
                ),
            )

        except Exception as e:
            logger.error(
                "Error calculating net value",
                extra={
                    "gross_usd": gross_usd,
                    "platform": platform,
                    "tax_regime": tax_regime,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    def _calculate_platform_commission(self, gross_usd: float, platform: Platform) -> float:
        """
        Calculate platform commission based on tiered or flat structure.

        Upwork uses tiered pricing (20% first $500, then 10%, then 5%),
        while most other platforms use flat rates.

        Args:
            gross_usd: Gross project value in USD
            platform: Platform enum

        Returns:
            Commission amount in USD

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> # Upwork tiered: $1000 project
            >>> commission = calculator._calculate_platform_commission(1000.0, Platform.UPWORK)
            >>> # = $500 * 0.20 + $500 * 0.10 = $100 + $50 = $150
            >>> assert commission == 150.0
            >>> # Freelancer flat: 10% of $1000
            >>> commission = calculator._calculate_platform_commission(1000.0, Platform.FREELANCER)
            >>> assert commission == 100.0
        """
        commission_config = self.PLATFORM_COMMISSIONS.get(platform)

        if not commission_config:
            logger.warning(
                "Unknown platform, using default 10% commission",
                extra={"platform": platform.value},
            )
            return gross_usd * 0.10

        if commission_config["type"] == "flat":
            return gross_usd * commission_config["rate"]

        elif commission_config["type"] == "tiered":
            total_commission = 0.0
            remaining = gross_usd
            previous_limit = 0.0

            for tier in commission_config["tiers"]:
                tier_limit = tier["limit"]
                tier_rate = tier["rate"]

                if remaining <= 0:
                    break

                # Calculate amount that falls in this tier
                tier_max = tier_limit - previous_limit
                tier_amount = min(remaining, tier_max)
                tier_commission = tier_amount * tier_rate

                total_commission += tier_commission
                remaining -= tier_amount
                previous_limit = tier_limit

            return total_commission

        return 0.0

    def _calculate_taxes(self, amount_brl: float, tax_regime: TaxRegime) -> float:
        """
        Calculate Brazilian income taxes based on regime.

        Different tax regimes:
        - MEI: Fixed monthly payment (R$ 66.60), not percentage-based
        - Others: Percentage of income

        Args:
            amount_brl: Amount in BRL to calculate tax on
            tax_regime: Tax regime enum

        Returns:
            Tax amount in BRL

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> # Simples Nacional: 6% of R$ 10,000
            >>> tax = calculator._calculate_taxes(10000.0, TaxRegime.SIMPLES_NACIONAL)
            >>> assert tax == 600.0
            >>> # MEI: Fixed R$ 66.60 regardless of amount
            >>> tax = calculator._calculate_taxes(10000.0, TaxRegime.MEI)
            >>> assert tax == 66.60
        """
        if tax_regime == TaxRegime.MEI:
            # MEI has fixed monthly payment (not percentage-based)
            return self.TAX_RATES[TaxRegime.MEI]
        else:
            # Percentage-based regimes
            tax_rate = self.TAX_RATES.get(tax_regime, 0.06)
            return amount_brl * tax_rate

    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Fetch real-time exchange rate from Banco Central do Brasil API.

        Caches rates in Redis for 1 hour to avoid excessive API calls
        and improve performance. Falls back to approximate rate if API fails.

        Args:
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'BRL')

        Returns:
            Exchange rate (cotação de venda / sell rate)

        Raises:
            No exceptions raised - uses fallback rate on errors

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> rate = calculator._get_exchange_rate("USD", "BRL")
            >>> assert rate > 0  # Should return positive rate
            >>> # With caching
            >>> calculator_cached = FreelancerFinancialCalculator(redis_client)
            >>> rate = calculator_cached._get_exchange_rate("USD", "BRL")
        """
        cache_key = f"forex:{from_currency}:{to_currency}"

        # Try cache first (if Redis available)
        if self.redis:
            try:
                cached_rate = self.redis.get(cache_key)
                if cached_rate:
                    logger.debug(
                        "Using cached exchange rate",
                        extra={
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "rate": float(cached_rate),
                        },
                    )
                    return float(cached_rate)
            except Exception as e:
                logger.warning(
                    "Error reading from Redis cache",
                    extra={"cache_key": cache_key, "error": str(e)},
                )

        # Fetch from Banco Central do Brasil API
        try:
            today = datetime.now().strftime("%m-%d-%Y")

            # Banco Central PTAX API endpoint
            url = (
                f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
                f"CotacaoMoedaDia(moeda=@moeda,dataCotacao=@dataCotacao)?"
                f"@moeda='{from_currency}'&@dataCotacao='{today}'&$format=json"
            )

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get("value"):
                raise ValueError("No exchange rate data returned from Banco Central API")

            # Get "cotação de venda" (sell rate - what you get when converting USD to BRL)
            rate = float(data["value"][0]["cotacaoVenda"])

            # Cache for 1 hour (rates update daily but cache reduces API load)
            if self.redis:
                try:
                    self.redis.setex(cache_key, 3600, str(rate))
                    logger.debug(
                        "Cached exchange rate",
                        extra={"cache_key": cache_key, "rate": rate, "ttl_seconds": 3600},
                    )
                except Exception as e:
                    logger.warning(
                        "Error caching exchange rate", extra={"cache_key": cache_key, "error": str(e)}
                    )

            logger.info(
                "Fetched exchange rate from Banco Central API",
                extra={
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "rate": rate,
                    "date": today,
                },
            )
            return rate

        except Exception as e:
            logger.error(
                "Error fetching exchange rate from Banco Central API - using fallback",
                extra={
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            # Fallback to approximate rate (typical USD→BRL rate)
            fallback_rate = 5.00
            logger.warning(
                "Using fallback exchange rate",
                extra={"rate": fallback_rate, "reason": "API fetch failed"},
            )
            return fallback_rate

    def _get_platform_enum(self, platform: str) -> Platform:
        """
        Convert platform string to enum with validation.

        Args:
            platform: Platform name as string

        Returns:
            Platform enum value

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> platform = calculator._get_platform_enum("upwork")
            >>> assert platform == Platform.UPWORK
            >>> platform = calculator._get_platform_enum("UPWORK")  # Case insensitive
            >>> assert platform == Platform.UPWORK
        """
        platform_lower = platform.lower()

        try:
            return Platform(platform_lower)
        except ValueError:
            logger.warning(
                "Unknown platform, using DIRECT (0% commission)",
                extra={"platform_input": platform, "fallback": "direct"},
            )
            return Platform.DIRECT

    def _get_tax_regime_enum(self, tax_regime: str) -> TaxRegime:
        """
        Convert tax regime string to enum with validation.

        Args:
            tax_regime: Tax regime name as string

        Returns:
            TaxRegime enum value

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> regime = calculator._get_tax_regime_enum("Simples_Nacional")
            >>> assert regime == TaxRegime.SIMPLES_NACIONAL
        """
        try:
            return TaxRegime(tax_regime)
        except ValueError:
            logger.warning(
                "Unknown tax regime, using Simples Nacional (6%)",
                extra={"tax_regime_input": tax_regime, "fallback": "Simples_Nacional"},
            )
            return TaxRegime.SIMPLES_NACIONAL

    def calculate_required_gross(
        self,
        desired_net_brl: float,
        platform: str = "upwork",
        tax_regime: str = "Simples_Nacional",
    ) -> FinancialBreakdown:
        """
        Calculate required gross USD to achieve desired net BRL (reverse calculation).

        Useful for pricing decisions: "I need R$ 10,000 net, how much should I charge?"

        Uses binary search to find the required gross amount since the
        relationship is non-linear due to tiered commissions.

        Args:
            desired_net_brl: Desired net amount in BRL (take-home pay)
            platform: Platform name
            tax_regime: Tax regime

        Returns:
            Complete financial breakdown with required_gross_usd field

        Raises:
            No exceptions raised - returns best approximation with warning if needed

        Examples:
            >>> calculator = FreelancerFinancialCalculator()
            >>> # Find required gross to get R$ 5000 net
            >>> result = calculator.calculate_required_gross(
            ...     desired_net_brl=5000.0,
            ...     platform="upwork",
            ...     tax_regime="Simples_Nacional"
            ... )
            >>> print(f"Charge: ${result['required_gross_usd']:.2f}")
            >>> print(f"You'll receive: R$ {result['net_brl']:.2f}")
            >>> # Compare platforms
            >>> upwork = calculator.calculate_required_gross(5000.0, "upwork")
            >>> freelancer = calculator.calculate_required_gross(5000.0, "freelancer")
            >>> print(f"Upwork: ${upwork['required_gross_usd']:.2f}")
            >>> print(f"Freelancer: ${freelancer['required_gross_usd']:.2f}")
        """
        # Use binary search to find required gross USD
        # This is needed because tiered commissions make it non-linear

        min_gross = 0.0
        max_gross = desired_net_brl * 2  # Start with 2x as conservative upper bound

        tolerance = 1.0  # R$ 1.00 tolerance is acceptable
        max_iterations = 50

        for iteration in range(max_iterations):
            mid_gross = (min_gross + max_gross) / 2

            result = self.calculate_net_value(mid_gross, platform, tax_regime)
            calculated_net = result["net_brl"]

            # Check if we're within tolerance
            if abs(calculated_net - desired_net_brl) < tolerance:
                result["desired_net_brl"] = desired_net_brl
                result["required_gross_usd"] = round(mid_gross, 2)
                logger.info(
                    "Found required gross amount",
                    extra={
                        "desired_net_brl": desired_net_brl,
                        "required_gross_usd": result["required_gross_usd"],
                        "actual_net_brl": calculated_net,
                        "iterations": iteration + 1,
                    },
                )
                return result

            # Adjust search bounds
            if calculated_net < desired_net_brl:
                min_gross = mid_gross
            else:
                max_gross = mid_gross

        # Return best approximation if didn't converge
        result = self.calculate_net_value(max_gross, platform, tax_regime)
        result["desired_net_brl"] = desired_net_brl
        result["required_gross_usd"] = round(max_gross, 2)
        result["warning"] = "Could not converge to exact value within tolerance"

        logger.warning(
            "Required gross calculation did not converge",
            extra={
                "desired_net_brl": desired_net_brl,
                "best_approximation_gross_usd": result["required_gross_usd"],
                "resulting_net_brl": result["net_brl"],
                "max_iterations_reached": max_iterations,
            },
        )

        return result
