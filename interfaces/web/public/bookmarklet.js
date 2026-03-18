/**
 * Charlee Project Extractor Bookmarklet v1.0
 *
 * This bookmarklet extracts project data from freelance platform pages
 * and sends it to the Charlee API for opportunity creation.
 *
 * Supported Platforms:
 * - Upwork
 * - Freelancer.com
 * - LinkedIn Jobs
 *
 * Usage:
 * 1. Save this code as a bookmark
 * 2. Navigate to a project page on a supported platform
 * 3. Click the bookmark
 * 4. Opportunity is created in Charlee
 *
 * @see docs/modulos-planejados/gestao-projetos-freelancers.md section 2.2.2
 */

(function () {
  'use strict';

  // Configuration - Update URLs for your deployment
  const FRONTEND_URL = window.CHARLEE_FRONTEND_URL || 'http://localhost:3000';
  const API_URL = window.CHARLEE_API_URL || 'http://localhost:8000';
  const API_ENDPOINT = '/api/v2/freelancer/opportunities/bookmarklet';

  /**
   * Decode HTML entities
   */
  function decodeHTML(html) {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  }

  // Get URL and detect platform
  const url = window.location.href;
  let project = {
    url: url,
    source: 'unknown',
    title: null,
    description: null,
    budget: null,
    skills: null,
    client_name: null,
    client_rating: null,
    client_country: null,
    client_projects_count: null,
    client_total_spent: null,
    client_payment_verified: null
  };

  /**
   * Extract data from Upwork project page
   */
  function extractUpwork() {
    project.source = 'upwork';

    // Title - multiple possible selectors (updated for current Upwork layout)
    const title =
      document.querySelector('h2[itemprop="title"]')?.innerText?.trim() ||
      document.querySelector('[data-test="job-title"]')?.innerText?.trim() ||
      document.querySelector('h1.job-title')?.innerText?.trim() ||
      document.querySelector('.job-details-header h1')?.innerText?.trim() ||
      document.querySelector('article h1')?.innerText?.trim() ||
      document.querySelector('main h1')?.innerText?.trim() ||
      document.querySelector('[class*="header"] h2')?.innerText?.trim() ||
      document.querySelector('h2')?.innerText?.trim() ||
      document.title.replace(' - Upwork', '').replace(' | Upwork', '').trim();
    project.title = title ? decodeHTML(title) : null;
    console.log('Charlee Bookmarklet - Title extracted:', project.title);

    // Description
    const desc =
      document.querySelector('[data-test="Description"]')?.innerText?.trim() ||
      document.querySelector('.job-description')?.innerText?.trim() ||
      document.querySelector('[data-test="UpCFeatureJobDescription"]')?.innerText?.trim() ||
      document.querySelector('[data-test="job-description"]')?.innerText?.trim() ||
      document.querySelector('article section')?.innerText?.trim();
    project.description = desc ? decodeHTML(desc) : null;
    console.log('Charlee Bookmarklet - Description length:', project.description?.length);

    // Budget
    project.budget =
      document.querySelector('[data-test="budget"]')?.innerText?.trim() ||
      document.querySelector('[data-test="BudgetAmount"]')?.innerText?.trim() ||
      document.querySelector('.job-budget')?.innerText?.trim();

    // Skills
    const skillElements =
      document.querySelectorAll('.skill-tag, [data-test="skill"], .air3-token') || [];
    project.skills = Array.from(skillElements)
      .map((s) => s.innerText.trim())
      .filter((s) => s)
      .join(', ');

    // Client info - try multiple selectors for Upwork's varying layouts
    project.client_name = document.querySelector('[data-test="client-name"]')?.innerText?.trim() ||
      document.querySelector('[data-cy="client-name"]')?.innerText?.trim() ||
      document.querySelector('.client-name')?.innerText?.trim();

    // Client rating - look for star rating or rating text (try many selectors)
    project.client_rating = document.querySelector('[data-test="client-rating"]')?.innerText?.trim() ||
      document.querySelector('[data-cy="buyer-rating"]')?.innerText?.trim() ||
      document.querySelector('.air3-rating-value')?.innerText?.trim() ||
      document.querySelector('[data-test="feedback-score"]')?.innerText?.trim() ||
      document.querySelector('.cfe-ui-rating')?.innerText?.trim();

    // Client country/location (try many selectors)
    project.client_country = document.querySelector('[data-test="client-location"]')?.innerText?.trim() ||
      document.querySelector('[data-cy="client-location"]')?.innerText?.trim() ||
      document.querySelector('[data-test="location"]')?.innerText?.trim() ||
      document.querySelector('.client-location')?.innerText?.trim();

    // Extract client history from the "About the client" section
    // Look for patterns like "14 jobs posted", "197 hires", "$324K total spent"
    const aboutClientSection = document.body.innerText;

    // Also get a cleaner version without extra whitespace for better pattern matching
    const cleanText = aboutClientSection.replace(/\s+/g, ' ');

    // Debug: Log a sample of the page text to help troubleshoot
    console.log('Charlee Bookmarklet - Searching for client info in page text...');
    console.log('Charlee Bookmarklet - Page contains "jobs posted":', cleanText.includes('jobs posted'));
    console.log('Charlee Bookmarklet - Page contains "total spent":', cleanText.includes('total spent'));
    console.log('Charlee Bookmarklet - Page contains "of" + "reviews":', cleanText.includes(' of ') && cleanText.includes('reviews'));
    console.log('Charlee Bookmarklet - Page contains "Payment" + "verified":', cleanText.toLowerCase().includes('payment') && cleanText.toLowerCase().includes('verified'));

    // Jobs posted - patterns: "14 jobs posted", "14 jobs\nposted"
    const jobsMatch = cleanText.match(/(\d+)\s*jobs?\s*posted/i);
    if (jobsMatch) {
      project.client_projects_count = parseInt(jobsMatch[1]);
      console.log('Charlee Bookmarklet - Found jobs posted:', jobsMatch[1]);
    }

    // Hires count - patterns: "197 hires", "14 hires, 65 active"
    if (!project.client_projects_count) {
      const hiresMatch = cleanText.match(/(\d+)\s*hires?(?:\s*,|\s|$)/i);
      if (hiresMatch) {
        project.client_projects_count = parseInt(hiresMatch[1]);
        console.log('Charlee Bookmarklet - Found hires:', hiresMatch[1]);
      }
    }

    // Total spent - patterns: "$324K total spent", "$56,000 total spent", "$324K+ total spent"
    const spentMatch = cleanText.match(/\$([0-9,.]+)\s*([KMB])?\+?\s*total\s*spent/i);
    if (spentMatch) {
      let amount = parseFloat(spentMatch[1].replace(/,/g, ''));
      const suffix = spentMatch[2]?.toUpperCase();
      if (suffix === 'K') amount *= 1000;
      else if (suffix === 'M') amount *= 1000000;
      else if (suffix === 'B') amount *= 1000000000;
      project.client_total_spent = amount;
      console.log('Charlee Bookmarklet - Found total spent:', amount);
    }

    // Payment verified - look for the green checkmark text
    const isVerified = cleanText.toLowerCase().includes('payment method verified') ||
      cleanText.toLowerCase().includes('payment verified');
    project.client_payment_verified = isVerified;
    console.log('Charlee Bookmarklet - Payment verified:', isVerified);

    // Rating - patterns: "4.93 of 68 reviews", "4.9 rating", etc.
    if (!project.client_rating) {
      // Most specific: "X.XX of X reviews" pattern (Upwork standard format)
      const reviewRatingMatch = cleanText.match(/(\d+\.?\d*)\s+of\s+\d+\s+reviews?/i);
      if (reviewRatingMatch) {
        project.client_rating = reviewRatingMatch[1];
        console.log('Charlee Bookmarklet - Found rating from reviews:', reviewRatingMatch[1]);
      } else {
        // Try: "Rating: X.X" or "X.X rating"
        const ratingTextMatch = cleanText.match(/rating[:\s]+(\d+\.?\d*)/i) ||
                                cleanText.match(/(\d+\.?\d*)\s+rating/i);
        if (ratingTextMatch) {
          project.client_rating = ratingTextMatch[1];
          console.log('Charlee Bookmarklet - Found rating from text:', ratingTextMatch[1]);
        } else {
          // Look for star emoji followed by number
          const starRatingMatch = cleanText.match(/[★⭐]\s*(\d+\.?\d*)/);
          if (starRatingMatch) {
            project.client_rating = starRatingMatch[1];
            console.log('Charlee Bookmarklet - Found rating from star:', starRatingMatch[1]);
          }
        }
      }
    }

    // Country - Look for location patterns in About the client section
    // Upwork shows country name followed by city and time
    if (!project.client_country) {
      // Common country names that appear in Upwork (case-insensitive search)
      const countries = ['Mexico', 'United States', 'United Kingdom', 'Canada', 'Australia',
                        'Germany', 'France', 'Spain', 'Brazil', 'India', 'Philippines',
                        'Argentina', 'Colombia', 'Chile', 'Peru', 'Ecuador', 'Venezuela',
                        'Pakistan', 'Bangladesh', 'Ukraine', 'Poland', 'Romania', 'Russia',
                        'China', 'Japan', 'South Korea', 'Vietnam', 'Indonesia', 'Malaysia',
                        'Singapore', 'Thailand', 'Netherlands', 'Belgium', 'Switzerland',
                        'Austria', 'Italy', 'Portugal', 'Ireland', 'Sweden', 'Norway',
                        'Denmark', 'Finland', 'Israel', 'Turkey', 'Egypt', 'Nigeria',
                        'South Africa', 'Kenya', 'Morocco', 'UAE', 'Saudi Arabia',
                        'New Zealand', 'Czech Republic', 'Hungary', 'Greece', 'Croatia'];

      for (const country of countries) {
        // Use word boundary check to avoid partial matches
        const regex = new RegExp('\\b' + country + '\\b', 'i');
        if (regex.test(cleanText)) {
          project.client_country = country;
          console.log('Charlee Bookmarklet - Found country:', country);
          break;
        }
      }
    }

    console.log('Charlee Bookmarklet - Client info:', {
      rating: project.client_rating,
      country: project.client_country,
      projects: project.client_projects_count,
      spent: project.client_total_spent,
      verified: project.client_payment_verified
    });
  }

  /**
   * Extract data from Freelancer.com project page
   */
  function extractFreelancer() {
    project.source = 'freelancer';

    // Title
    project.title =
      document.querySelector('h1.project-title')?.innerText?.trim() ||
      document.querySelector('.PageProjectViewLogout-header h1')?.innerText?.trim() ||
      document.querySelector('[data-project-title]')?.innerText?.trim();

    // Description
    project.description =
      document.querySelector('.project-description')?.innerText?.trim() ||
      document.querySelector('.PageProjectViewLogout-description')?.innerText?.trim() ||
      document.querySelector('[data-project-description]')?.innerText?.trim();

    // Budget
    project.budget =
      document.querySelector('.budget-amount')?.innerText?.trim() ||
      document.querySelector('.PageProjectViewLogout-budget')?.innerText?.trim() ||
      document.querySelector('[data-budget]')?.innerText?.trim();

    // Skills
    const skillElements = document.querySelectorAll('.skill-name, .TagItem, .project-skill') || [];
    project.skills = Array.from(skillElements)
      .map((s) => s.innerText.trim())
      .filter((s) => s)
      .join(', ');

    // Client info
    project.client_name = document.querySelector('.employer-name')?.innerText?.trim();
    project.client_rating = document.querySelector('.employer-rating')?.innerText?.trim();
    project.client_country = document.querySelector('.employer-country')?.innerText?.trim();
  }

  /**
   * Extract data from LinkedIn Jobs page
   */
  function extractLinkedIn() {
    project.source = 'linkedin';

    // Title
    project.title =
      document.querySelector('.job-details-jobs-unified-top-card__job-title')?.innerText?.trim() ||
      document.querySelector('.topcard__title')?.innerText?.trim() ||
      document.querySelector('h1.jobs-unified-top-card__job-title')?.innerText?.trim();

    // Description
    project.description =
      document.querySelector('.jobs-description__content')?.innerText?.trim() ||
      document.querySelector('.description__text')?.innerText?.trim() ||
      document.querySelector('[data-test="job-description"]')?.innerText?.trim();

    // Company name as client
    project.client_name =
      document.querySelector('.job-details-jobs-unified-top-card__company-name')?.innerText?.trim() ||
      document.querySelector('.topcard__org-name-link')?.innerText?.trim();

    // Location as country
    project.client_country =
      document.querySelector('.job-details-jobs-unified-top-card__workplace-type')?.innerText?.trim() ||
      document.querySelector('.topcard__flavor--bullet')?.innerText?.trim();

    // Skills from job insights if available
    const skillElements = document.querySelectorAll('.job-details-how-you-match__skills-item') || [];
    project.skills = Array.from(skillElements)
      .map((s) => s.innerText.trim())
      .filter((s) => s)
      .join(', ');
  }

  /**
   * Detect platform and extract data
   */
  function detectAndExtract() {
    if (url.includes('upwork.com')) {
      extractUpwork();
    } else if (url.includes('freelancer.com')) {
      extractFreelancer();
    } else if (url.includes('linkedin.com/jobs')) {
      extractLinkedIn();
    } else {
      // Unknown platform - try generic extraction
      project.source = 'generic';
      project.title = document.querySelector('h1')?.innerText?.trim() || document.title;
      project.description =
        document.querySelector('article')?.innerText?.trim() ||
        document.querySelector('main')?.innerText?.substring(0, 5000);

      // Try to extract client/company info from the page text
      const pageText = document.body.innerText;

      // Look for common patterns for client info
      const ratingMatch = pageText.match(/(\d+\.?\d*)\s*(star|estrela|rating|avaliação)/i) ||
                          pageText.match(/(rating|avaliação)[:\s]*(\d+\.?\d*)/i);
      if (ratingMatch) {
        project.client_rating = ratingMatch[1] || ratingMatch[2];
      }

      // Look for jobs/projects count
      const jobsMatch = pageText.match(/(\d+)\s*(jobs?\s*posted|projetos?\s*postados|hires?|contratações)/i);
      if (jobsMatch) {
        project.client_projects_count = parseInt(jobsMatch[1]);
      }

      // Look for total spent
      const spentMatch = pageText.match(/\$([0-9,.]+)([KMB]?)\s*(total\s*spent|gasto\s*total)/i);
      if (spentMatch) {
        let amount = parseFloat(spentMatch[1].replace(/,/g, ''));
        const suffix = spentMatch[2]?.toUpperCase();
        if (suffix === 'K') amount *= 1000;
        else if (suffix === 'M') amount *= 1000000;
        project.client_total_spent = amount;
      }

      // Look for country/location
      const locationMatch = pageText.match(/(location|país|country|localização)[:\s]*([A-Za-z\s]+)/i);
      if (locationMatch) {
        project.client_country = locationMatch[2]?.trim().substring(0, 50);
      }

      // Payment verified
      project.client_payment_verified = pageText.toLowerCase().includes('payment verified') ||
        pageText.toLowerCase().includes('pagamento verificado');

      console.log('Charlee Bookmarklet - Generic extraction client info:', {
        rating: project.client_rating,
        country: project.client_country,
        projects: project.client_projects_count,
        spent: project.client_total_spent,
        verified: project.client_payment_verified
      });
    }
  }

  /**
   * Log extracted data for debugging
   */
  function logExtractedData() {
    console.log('=== Charlee Bookmarklet - Extracted Data ===');
    console.log('Source:', project.source);
    console.log('URL:', project.url);
    console.log('Title:', project.title || '(not found)');
    console.log('Description:', project.description ? `${project.description.substring(0, 100)}...` : '(not found)');
    console.log('Budget:', project.budget || '(not found)');
    console.log('Skills:', project.skills || '(not found)');
    console.log('==========================================');
  }

  /**
   * Get auth token from localStorage (assumes Charlee stores it there)
   */
  function getAuthToken() {
    // Try different possible storage keys
    return (
      localStorage.getItem('charlee_token') ||
      localStorage.getItem('auth_token') ||
      localStorage.getItem('token') ||
      sessionStorage.getItem('charlee_token')
    );
  }

  /**
   * Send data to Charlee API
   */
  async function sendToCharlee() {
    const token = getAuthToken();

    if (!token) {
      // Encode data for URL transmission
      const dataStr = JSON.stringify(project);
      const dataEncoded = encodeURIComponent(dataStr);
      console.log('[Charlee Bookmarklet] Opening login with encoded data...');
      window.open(`${FRONTEND_URL}/login.html?bookmarklet_data=${dataEncoded}`, 'charlee_import');
      return;
    }

    try {
      const response = await fetch(`${API_URL}${API_ENDPOINT}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(project)
      });

      if (response.ok) {
        const result = await response.json();
        showNotification('success', result.message || 'Opportunity imported!');
      } else if (response.status === 401) {
        // Auth expired - redirect to login
        const dataStr = JSON.stringify(project);
        const dataEncoded = encodeURIComponent(dataStr);
        window.open(`${FRONTEND_URL}/login.html?bookmarklet_data=${dataEncoded}`, 'charlee_login');
      } else {
        const error = await response.json();
        showNotification('error', error.detail || 'Failed to import');
      }
    } catch (error) {
      console.error('Charlee Bookmarklet Error:', error);
      // Fallback: open Charlee with data
      const dataStr = JSON.stringify(project);
      const dataEncoded = encodeURIComponent(dataStr);
      window.open(`${FRONTEND_URL}/login.html?bookmarklet_data=${dataEncoded}`, 'charlee_import');
    }
  }

  /**
   * Show notification to user
   */
  function showNotification(type, message) {
    const colors = {
      success: '#10B981',
      error: '#EF4444',
      info: '#3B82F6'
    };

    const div = document.createElement('div');
    div.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 24px;
      background: ${colors[type] || colors.info};
      color: white;
      border-radius: 8px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      z-index: 999999;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideIn 0.3s ease-out;
    `;

    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);

    div.textContent = message;
    document.body.appendChild(div);

    setTimeout(() => {
      div.remove();
      style.remove();
    }, 4000);
  }

  // Main execution
  try {
    detectAndExtract();
    logExtractedData();

    // Validate minimum data
    if (!project.title && !project.description) {
      showNotification('error', 'Could not extract project data from this page');
      return;
    }

    // Show loading
    showNotification('info', 'Importing to Charlee...');

    // Send to API
    sendToCharlee();
  } catch (error) {
    console.error('Charlee Bookmarklet Error:', error);
    showNotification('error', 'Error extracting data');
  }
})();
