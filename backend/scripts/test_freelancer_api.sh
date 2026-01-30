#!/bin/bash
# Freelancer API Testing Script (cURL)
# Usage: ./scripts/test_freelancer_api.sh
#
# Prerequisites:
# 1. Backend running: python3 -m uvicorn main:app --reload
# 2. Database seeded with test user

set -e

BASE_URL="http://localhost:8000"
TOKEN="your_jwt_token_here"  # Replace with actual JWT token

echo "========================================="
echo "  🚀 Freelancer API Testing with cURL"
echo "========================================="
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo "========================================="
    echo "  $1"
    echo "========================================="
    echo ""
}

# Function to make authenticated requests
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ -z "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            "$BASE_URL$endpoint" | jq '.'
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint" | jq '.'
    fi
}

print_section "1. Health Check"
curl -s "$BASE_URL/health" | jq '.'

print_section "2. Test Duplication Prevention (RN09)"
echo "Creating opportunity #1..."
api_call POST "/api/v1/opportunities" '{
  "title": "Python Backend API Development",
  "description": "Need a Python FastAPI developer for building RESTful APIs",
  "client_budget": 5000,
  "platform_name": "upwork",
  "external_id": "upwork_001"
}'

echo ""
echo "Testing duplicate detection (should detect as duplicate)..."
api_call POST "/api/v1/opportunities/check-duplicate" '{
  "title": "Python Backend API Development",
  "description": "Looking for FastAPI expert to build REST APIs",
  "platform_name": "upwork",
  "external_id": "upwork_002"
}'

print_section "3. Test Risk Assessment (RN12)"
echo "Assessing high-risk client..."
api_call POST "/api/v1/risk/assess" '{
  "client_rating": 2.5,
  "client_projects_count": 2,
  "project_description": "Need this ASAP! Budget is flexible but looking for cheapest option.",
  "client_payment_verified": false,
  "client_country": "Unknown"
}'

echo ""
echo "Assessing low-risk client..."
api_call POST "/api/v1/risk/assess" '{
  "client_rating": 4.8,
  "client_projects_count": 50,
  "project_description": "Looking for experienced Python developer for 3-month project.",
  "client_payment_verified": true,
  "client_country": "United States"
}'

print_section "4. Test Financial Calculator (RN11)"
echo "Calculating net income (USD → BRL + taxes)..."
api_call POST "/api/v1/financial/calculate" '{
  "gross_usd": 5000,
  "platform": "upwork",
  "tax_regime": "simples_nacional",
  "include_breakdown": true
}'

print_section "5. Test Pricing Learner"
echo "Analyzing pricing performance..."
api_call GET "/api/v1/learning/pricing/performance?days=90"

echo ""
echo "Suggesting pricing adjustments..."
api_call GET "/api/v1/learning/pricing/suggest-adjustment"

print_section "6. Test Rejection Pattern Learner"
echo "Analyzing rejection patterns..."
api_call GET "/api/v1/learning/rejection/patterns?days=90"

echo ""
echo "Suggesting risk weight adjustments..."
api_call GET "/api/v1/learning/rejection/suggest-weights"

print_section "7. Test Hourly Rate Optimizer"
echo "Analyzing acceptance by rate range..."
api_call GET "/api/v1/learning/rate/analyze?days=90"

echo ""
echo "Suggesting rate adjustment..."
api_call GET "/api/v1/learning/rate/suggest?target_acceptance_rate=0.60"

print_section "8. Test Integration Service (Full Pipeline)"
echo "Processing opportunity through full pipeline..."
api_call POST "/api/v1/integration/process-opportunity" '{
  "title": "AI/ML Model Development",
  "description": "Looking for ML engineer to build recommendation system",
  "client_budget": 8000,
  "platform_name": "upwork",
  "external_id": "upwork_ml_001",
  "client_rating": 4.5,
  "client_projects_count": 25,
  "client_payment_verified": true
}'

print_section "✅ All API Tests Completed!"
echo "Next steps:"
echo "  1. Import into Postman: File > Import > paste these cURL commands"
echo "  2. Replace \$TOKEN with actual JWT token from /auth/login"
echo "  3. Check responses and status codes"
echo "  4. View documentation at http://localhost:8000/docs"
