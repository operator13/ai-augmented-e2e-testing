"""
Error Reporter - Generates reports for filtered website errors with JIRA formatting.

This module tracks known website issues, generates JSON reports, and creates
JIRA-formatted bug tickets ready for submission.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


class JiraFormatter:
    """Formats error reports for JIRA bug tickets."""

    @staticmethod
    def format_bug_report(error_category: str, errors: List[Dict], test_context: Dict) -> str:
        """
        Generate JIRA-formatted bug report for a specific error category.

        Args:
            error_category: Type of error (e.g., 'video_playback', 'network_503')
            errors: List of error details
            test_context: Test execution context (test name, URL, timestamp)

        Returns:
            JIRA-formatted markdown string
        """

        # Map error categories to JIRA bug templates
        templates = {
            'video_playback': JiraFormatter._video_playback_template,
            'network_503': JiraFormatter._network_503_template,
            'dealer_lookup': JiraFormatter._dealer_lookup_template,
            'js_undefined': JiraFormatter._js_undefined_template,
            'image_403': JiraFormatter._image_403_template,
        }

        template_func = templates.get(error_category, JiraFormatter._generic_template)
        return template_func(errors, test_context)

    @staticmethod
    def _video_playback_template(errors: List[Dict], context: Dict) -> str:
        """JIRA template for video playback errors."""
        sample_error = errors[0]

        return f"""h1. Video Autoplay Error: play() interrupted by pause()

*Priority:* Medium
*Component:* Frontend / Media Player
*Affects Version:* Production Website
*Environment:* {context.get('browser', 'Chrome')} on {context.get('platform', 'macOS')}

h2. Summary

Video autoplay functionality is causing JavaScript console errors due to race condition between play() and pause() calls. This error occurs {len(errors)} times during page navigation.

h2. Description

The website's video player attempts to autoplay videos, but the play() Promise is immediately interrupted by a pause() call, resulting in uncaught Promise rejections in the browser console.

*Error Message:*
{{code:javascript}}
Uncaught (in promise) DOMException: The play() request was interrupted by a call to pause().
{{code}}

*Reference:* https://goo.gl/LdLk22 (Chrome Developer Documentation)

h2. Steps to Reproduce

# Open Chrome Browser
# Open DevTools (F12) and navigate to *Console* tab
# Clear console (trash icon)
# Navigate to: {sample_error.get('page_url', 'https://www.toyota.com/camry')}
# Observe multiple console errors appearing during page load
# Navigate to Gallery section: {{#gallery}}
# Observe additional errors
# Navigate to Features section: {{#features}}
# Observe additional errors

h2. Expected Behavior

Video autoplay should either:
* Successfully autoplay without errors, OR
* Gracefully handle autoplay restrictions with proper error handling (try/catch on play() Promise)

h2. Actual Behavior

Multiple uncaught Promise rejections appear in console:
* {len(errors)} errors detected during test execution
* Errors occur on: {', '.join(set(e.get('page_url', 'unknown') for e in errors[:3]))}

h2. Technical Details

*First Occurrence:*
* Timestamp: {errors[0].get('timestamp', 'N/A')}
* Page: {errors[0].get('page_url', 'N/A')}

*Error Pattern:*
* Occurs during initial page load
* Occurs when navigating between page sections
* Suggests race condition in video initialization code

h2. Impact

* *Severity:* Low-Medium
* *User Impact:* No visible user impact - videos still function, but console errors may affect debugging and performance monitoring
* *Frequency:* Occurs consistently on every page load

h2. Suggested Fix

{{code:javascript}}
// Current problematic code pattern:
video.play();  // Returns a Promise
video.pause(); // Called immediately

// Recommended fix:
video.play()
  .then(() => {{
    // Only pause if play succeeded
    if (shouldPause) {{
      video.pause();
    }}
  }})
  .catch(err => {{
    console.debug('Autoplay prevented:', err);
    // Gracefully handle autoplay restrictions
  }});
{{code}}

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
*Total Occurrences:* {len(errors)}

h2. Additional Notes

This is a known browser behavior related to autoplay restrictions. Modern browsers limit video autoplay to improve user experience. The error indicates the website's video player needs better Promise handling.

*Browser Autoplay Policies:*
* Chrome: https://developer.chrome.com/blog/autoplay/
* Firefox: https://developer.mozilla.org/en-US/docs/Web/Media/Autoplay_guide
"""

    @staticmethod
    def _network_503_template(errors: List[Dict], context: Dict) -> str:
        """JIRA template for HTTP 503 errors."""
        sample_error = errors[0]
        failed_urls = set(e.get('details', {}).get('url', 'unknown') for e in errors)

        return f"""h1. Third-Party Advertising Pixel Failures (HTTP 503)

*Priority:* Low
*Component:* Marketing / Third-Party Integrations
*Affects Version:* Production Website
*Environment:* All Browsers

h2. Summary

Third-party advertising tracking pixels from Neustar AdAdvisor (d.agkn.com) are returning HTTP 503 Service Unavailable errors. This affects {len(errors)} tracking requests during page navigation.

h2. Description

The website loads tracking pixels from d.agkn.com (Neustar AdAdvisor) for advertising analytics. These requests are consistently failing with HTTP 503 errors, indicating the third-party service is unavailable or rate-limiting requests.

*Failed Requests:*
{chr(10).join(f'* {url}' for url in list(failed_urls)[:5])}

h2. Steps to Reproduce

# Open Chrome Browser
# Open DevTools (F12) and navigate to *Network* tab
# Filter by domain: {{d.agkn.com}}
# Navigate to: https://www.toyota.com
# Observe red 503 errors in network panel
# Click any vehicle link (e.g., RAV4)
# Observe additional 503 errors

*Alternative method:*
# Open DevTools → Console tab
# Navigate to: https://www.toyota.com
# Look for network error messages with "503" and "d.agkn.com"

h2. Expected Behavior

* Tracking pixels should load successfully (HTTP 200), OR
* Failed tracking pixels should fail silently without affecting page functionality

h2. Actual Behavior

* {len(errors)} HTTP 503 errors detected
* Errors appear in browser console and network panel
* Service: d.agkn.com (Neustar AdAdvisor)
* Status: 503 Service Unavailable

h2. Technical Details

*Service Information:*
* Provider: Neustar AdAdvisor (formerly Aggregate Knowledge)
* Purpose: Advertising tracking and attribution
* Delivery: CloudFront CDN

*Error Details:*
* Status Code: 503
* Response Header: {{X-Cache: Error from cloudfront}}
* First Occurrence: {errors[0].get('timestamp', 'N/A')}

*Affected Pages:*
{chr(10).join(f'* {url}' for url in set(e.get('page_url', 'unknown') for e in errors[:5]))}

h2. Impact

* *Severity:* Low
* *User Impact:* None - page functionality unaffected
* *Business Impact:* Advertising tracking/attribution data may be incomplete
* *Frequency:* Consistent failures during test period

h2. Root Cause

Likely causes:
# Third-party service outage
# Rate limiting from d.agkn.com
# CloudFront configuration issues
# Expired or invalid tracking pixel URLs

h2. Recommended Actions

# *Verify service status* - Check with Neustar AdAdvisor if service is operational
# *Review pixel configuration* - Ensure tracking pixel URLs are current
# *Implement error handling* - Suppress console errors from failed tracking pixels
# *Consider alternatives* - If service is unreliable, evaluate alternative tracking solutions
# *Add monitoring* - Set up alerts for tracking pixel failures

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
*Total Failures:* {len(errors)}
*Unique URLs Failed:* {len(failed_urls)}

h2. Workaround

These errors do not affect website functionality. Tracking pixel failures are typically non-blocking and fail silently for end users. However, they should be addressed to ensure complete advertising analytics data.
"""

    @staticmethod
    def _dealer_lookup_template(errors: List[Dict], context: Dict) -> str:
        """JIRA template for dealer lookup API errors."""
        sample_error = errors[0]
        dealer_codes = set()
        for e in errors:
            msg = e.get('message', '')
            # Extract dealer code from message
            if 'dealer code:' in msg:
                code = msg.split('dealer code:')[-1].strip()
                dealer_codes.add(code)

        return f"""h1. Dealer Lookup API Failure: Unable to Retrieve Dealer Details

*Priority:* Medium
*Component:* Backend API / Dealer Services
*Affects Version:* Production Website
*Environment:* All Browsers

h2. Summary

The dealer lookup API is failing to retrieve dealer information for specific dealer codes. This results in uncaught Promise rejections in the browser console, occurring {len(errors)} times during normal page navigation.

h2. Description

When users visit the Toyota website, the system attempts to fetch dealer information based on location/dealer code. The API request is failing for certain dealer codes, causing JavaScript errors.

*Error Message:*
{{code:javascript}}
Uncaught (in promise) Unable to retrieve dealer details for dealer code: {', '.join(dealer_codes)}
{{code}}

*Source:* clientlib-sitev2.min.js

h2. Steps to Reproduce

# Open Chrome Browser with DevTools (F12)
# Navigate to *Console* tab
# Clear console
# Navigate to: https://www.toyota.com
# Wait for page to fully load
# Observe error: "Unable to retrieve dealer details for dealer code: [code]"
# Navigate to any vehicle page (e.g., /camry)
# Observe additional errors may appear

h2. Expected Behavior

* Dealer lookup API should successfully return dealer information, OR
* API failures should be handled gracefully with fallback behavior
* No uncaught Promise rejections in console

h2. Actual Behavior

* Uncaught Promise rejection appears in console
* Failed dealer codes: {', '.join(dealer_codes)}
* {len(errors)} failures detected during test

h2. Technical Details

*API Endpoint:* (Assumed to be dealer lookup service)
*Failed Dealer Codes:*
{chr(10).join(f'* {code}' for code in dealer_codes)}

*Error Location:*
* File: clientlib-sitev2.min.js
* Type: Promise rejection (async operation failure)

*First Occurrence:*
* Timestamp: {errors[0].get('timestamp', 'N/A')}
* Page: {errors[0].get('page_url', 'N/A')}

h2. Impact

* *Severity:* Medium
* *User Impact:* Users may not see local dealer information
* *Frequency:* Occurs consistently for specific dealer codes
* *Business Impact:* May affect dealer locator functionality and lead generation

h2. Possible Root Causes

# Invalid or outdated dealer codes in database
# Dealer API service unavailable or timing out
# Missing error handling in dealer lookup code
# Geographic/location detection issues
# Dealer database synchronization problems

h2. Recommended Actions

# *Verify dealer codes exist* - Check if dealer codes {', '.join(dealer_codes)} are valid in dealer database
# *Add error handling* - Implement try/catch for dealer lookup Promise
# *Add fallback behavior* - Show generic dealer search if specific lookup fails
# *Add logging* - Track which dealer codes are failing for investigation
# *API health check* - Verify dealer API service is operational

h2. Suggested Fix

{{code:javascript}}
// Add proper error handling
async function getDealerDetails(dealerCode) {{
  try {{
    const response = await fetchDealerAPI(dealerCode);
    return response;
  }} catch (error) {{
    console.warn(`Dealer lookup failed for code ${{dealerCode}}:`, error);
    // Fallback: show dealer search or generic message
    return showDealerSearch();
  }}
}}
{{code}}

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
*Total Occurrences:* {len(errors)}
*Failed Codes:* {', '.join(dealer_codes)}
"""

    @staticmethod
    def _js_undefined_template(errors: List[Dict], context: Dict) -> str:
        """JIRA template for JavaScript undefined property errors."""
        sample_error = errors[0]

        return f"""h1. JavaScript Error: Cannot Read Properties of Undefined

*Priority:* Medium
*Component:* Frontend / JavaScript
*Affects Version:* Production Website - RAV4 Page
*Environment:* All Browsers

h2. Summary

JavaScript errors are occurring on the RAV4 vehicle page when attempting to access properties (reading 'remove' and 'destroy') on undefined objects. This indicates a potential null reference issue in the page's JavaScript code.

h2. Description

When navigating to the RAV4 page, JavaScript errors appear in the console indicating that code is attempting to call methods on undefined objects. This occurs {len(errors)} times during page load and interaction.

*Error Messages:*
{{code:javascript}}
Cannot read properties of undefined (reading 'remove')
Cannot read properties of undefined (reading 'destroy')
{{code}}

h2. Steps to Reproduce

# Open Chrome Browser with DevTools (F12)
# Navigate to *Console* tab
# Clear console
# Navigate to: https://www.toyota.com
# Click on "Vehicles" in navigation
# Click on "RAV4" link
# Wait for RAV4 page to load
# Observe JavaScript errors in console

h2. Expected Behavior

* All JavaScript code should execute without errors
* Proper null/undefined checks before accessing object properties
* Graceful handling if expected DOM elements or objects are missing

h2. Actual Behavior

* Multiple "Cannot read properties of undefined" errors
* Errors occur during RAV4 page load
* Functions attempting to call .remove() and .destroy() on undefined objects
* {len(errors)} errors detected during test

h2. Technical Details

*Error Properties:*
* Property access attempts: 'remove', 'destroy'
* Indicates missing null checks before method calls
* Likely related to DOM element cleanup or component lifecycle

*Affected Page:*
* URL: https://www.toyota.com/rav4/
* Timestamp: {errors[0].get('timestamp', 'N/A')}

*Error Pattern:*
{chr(10).join(f"* {e.get('message', 'N/A')}" for e in errors[:5])}

h2. Impact

* *Severity:* Medium
* *User Impact:* Page appears to function normally, but JavaScript errors may cause:
  * Failed component cleanup
  * Memory leaks (if destroy() is for cleanup)
  * Potential UI glitches in certain scenarios
* *Frequency:* Consistent on RAV4 page load

h2. Possible Root Causes

# DOM element expected but not present on page
# Async race condition - code executing before elements ready
# Component lifecycle issue - destroy() called on uninitialized component
# Missing feature detection or existence check
# Copy-paste code from another page where elements do exist

h2. Recommended Actions

# *Add null checks* - Verify objects exist before accessing properties
# *Review RAV4 page code* - Identify where .remove() and .destroy() are called
# *Add defensive coding* - Use optional chaining or guard clauses
# *Test fix thoroughly* - Ensure no regression on other vehicle pages
# *Code review* - Check if similar pattern exists on other pages

h2. Suggested Fix

{{code:javascript}}
// Current problematic code:
someElement.remove();
someComponent.destroy();

// Recommended fix:
if (someElement) {{
  someElement.remove();
}}

if (someComponent && typeof someComponent.destroy === 'function') {{
  someComponent.destroy();
}}

// Or using optional chaining:
someElement?.remove();
someComponent?.destroy();
{{code}}

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
*Total Errors:* {len(errors)}
*Page:* RAV4 Vehicle Page

h2. Additional Notes

This error pattern is common when:
* Code expects certain elements that aren't present on all variations of the page
* Mobile vs desktop differences
* A/B testing causing different DOM structures
* Feature flags changing page structure

The fix should include proper existence checks and handle both cases gracefully.
"""

    @staticmethod
    def _image_403_template(errors: List[Dict], context: Dict) -> str:
        """JIRA template for image 403 Forbidden errors."""
        sample_error = errors[0]
        failed_images = set(e.get('details', {}).get('url', 'unknown') for e in errors)

        return f"""h1. Image Asset Loading Failure: HTTP 403 Forbidden

*Priority:* High
*Component:* CDN / Image Assets
*Affects Version:* Production Website
*Environment:* All Browsers

h2. Summary

Product images from Toyota's asset CDN (tmna.aemassets.toyota.com) are returning HTTP 403 Forbidden errors, preventing vehicle images from loading correctly. This affects {len(errors)} image requests.

h2. Description

Vehicle product images hosted on Toyota's AEM Assets CDN are failing to load with 403 Forbidden errors. This indicates either:
* CDN access control issues
* Invalid/expired image URLs
* Missing authentication/authorization headers
* CORS policy restrictions

*Failed Image URLs:*
{chr(10).join(f'* {url[:100]}...' for url in list(failed_images)[:3])}

h2. Steps to Reproduce

# Open Chrome Browser with DevTools (F12)
# Navigate to *Network* tab
# Filter by: {{Img}} or {{tmna.aemassets.toyota.com}}
# Navigate to: https://www.toyota.com/camry
# Observe red 403 Forbidden errors in network panel
# Note which images are failing to load
# Check page visually for missing images

h2. Expected Behavior

* All vehicle product images should load successfully (HTTP 200)
* Images should be visible on the page
* No broken image placeholders

h2. Actual Behavior

* {len(errors)} image requests returning HTTP 403 Forbidden
* Images may not display or show broken image icons
* CDN: tmna.aemassets.toyota.com
* Error occurs on: {', '.join(set(e.get('page_url', 'unknown') for e in errors[:3]))}

h2. Technical Details

*CDN Information:*
* Host: tmna.aemassets.toyota.com
* Image Service: Adobe Experience Manager Assets
* Status Code: 403 Forbidden
* Cache-Control: max-age=0, no-cache, no-store

*Image URL Pattern:*
{{code}}
https://tmna.aemassets.toyota.com/is/image/toyota/toyota/jellies/max/2026/camry/[params]
{{code}}

*First Failure:*
* Timestamp: {errors[0].get('timestamp', 'N/A')}
* Page: {errors[0].get('page_url', 'N/A')}

h2. Impact

* *Severity:* High
* *User Impact:* Vehicle images not displaying - significant UX issue
* *Business Impact:*
  * Users cannot see product images
  * May affect conversion rates
  * Poor user experience
* *Frequency:* Consistent failures

h2. Possible Root Causes

# *CDN access control* - Referrer policy or origin restrictions
# *Invalid image URLs* - Incorrect path or parameters
# *Authentication required* - Missing auth headers
# *Image deleted/moved* - Assets no longer exist at that path
# *Rate limiting* - Too many requests from same IP
# *CORS policy* - Cross-origin restrictions

h2. Recommended Actions (URGENT)

# *Verify image URLs* - Test URLs directly in browser
# *Check CDN config* - Review AEM Assets security settings
# *Review access controls* - Ensure public images are accessible
# *Check image paths* - Verify images exist in AEM
# *Monitor CDN* - Check Adobe AEM Assets service status
# *Rollback if recent change* - If images worked previously

h2. Diagnostic Steps

{{code:bash}}
# Test image URL directly
curl -I "https://tmna.aemassets.toyota.com/is/image/toyota/toyota/jellies/max/2026/camry/..."

# Check response headers
# Look for: Access-Control-Allow-Origin, Cache-Control, etc.
{{code}}

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
*Total Failures:* {len(errors)}
*Unique Images Failed:* {len(failed_images)}

h2. Business Priority

This is a HIGH priority issue as it directly impacts the visual presentation of products to customers. Vehicle images are critical for user engagement and purchase decisions.
"""

    @staticmethod
    def _generic_template(errors: List[Dict], context: Dict) -> str:
        """Generic JIRA template for unknown error types."""
        sample_error = errors[0]

        return f"""h1. Website Error Detected: {sample_error.get('type', 'Unknown Error')}

*Priority:* Medium
*Component:* Frontend
*Affects Version:* Production Website
*Environment:* {context.get('browser', 'Chrome')} on {context.get('platform', 'macOS')}

h2. Summary

Automated testing detected {len(errors)} errors of type: {sample_error.get('type', 'unknown')} during website navigation.

h2. Description

*Error Message:*
{{code}}
{sample_error.get('message', 'No message available')}
{{code}}

h2. Steps to Reproduce

# Navigate to: {sample_error.get('page_url', 'https://www.toyota.com')}
# Open browser DevTools Console
# Observe error messages

h2. Technical Details

*First Occurrence:*
* Timestamp: {errors[0].get('timestamp', 'N/A')}
* Page: {errors[0].get('page_url', 'N/A')}
* Severity: {errors[0].get('severity', 'N/A')}

*Total Occurrences:* {len(errors)}

h2. Test Evidence

*Test Name:* {context.get('test_name', 'N/A')}
*Test Date:* {context.get('test_date', 'N/A')}
"""


class ErrorReporter:
    """Generates JSON reports and JIRA tickets for filtered website errors."""

    def __init__(self, report_dir: str = "reports/filtered_errors"):
        """
        Initialize error reporter.

        Args:
            report_dir: Directory to save reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def categorize_errors(self, anomalies: List) -> Dict[str, List[Dict]]:
        """
        Categorize anomalies into known error types.

        Args:
            anomalies: List of Anomaly objects from AnomalyDetector

        Returns:
            Dictionary mapping error category to list of error details
        """
        categorized = defaultdict(list)

        for anomaly in anomalies:
            message_lower = str(anomaly.message).lower()

            # Categorize based on error message patterns
            if 'play()' in message_lower and 'pause()' in message_lower:
                category = 'video_playback'
            elif 'http 503' in message_lower or 'd.agkn.com' in message_lower:
                category = 'network_503'
            elif '12166' in anomaly.message or '12161' in anomaly.message or 'dealer' in message_lower:
                category = 'dealer_lookup'
            elif 'cannot read properties of undefined' in message_lower:
                category = 'js_undefined'
            elif 'http 403' in message_lower or '403' in str(getattr(anomaly, 'details', {})):
                category = 'image_403'
            elif 'awswaf-captcha' in message_lower or 'customelementregistry' in message_lower:
                category = 'waf_captcha'
            elif 'mutationobserver' in message_lower:
                category = 'mutation_observer'
            else:
                category = 'other'

            # Convert anomaly to dictionary
            error_dict = {
                'type': getattr(anomaly, 'type', 'unknown'),
                'severity': getattr(anomaly, 'severity', 'unknown'),
                'message': anomaly.message,
                'timestamp': getattr(anomaly, 'timestamp', datetime.now().isoformat()),
                'page_url': getattr(anomaly, 'page_url', 'unknown'),
                'details': getattr(anomaly, 'details', {})
            }

            categorized[category].append(error_dict)

        return dict(categorized)

    def generate_consolidated_jira_ticket(self, categorized: Dict, test_context: Dict) -> str:
        """
        Generate ONE consolidated JIRA ticket with all error categories.

        Args:
            categorized: Dictionary of categorized errors
            test_context: Test execution context

        Returns:
            JIRA-formatted string with all issues
        """
        total_errors = sum(len(errors) for errors in categorized.values())

        ticket = f"""h1. Toyota Website - Multiple Issues Detected During Automated Testing

*Priority:* Medium
*Component:* Frontend / Backend / Third-Party Services
*Affects Version:* Production Website
*Environment:* {test_context.get('browser', 'Chromium')} on {test_context.get('platform', 'macOS')}
*Test Date:* {test_context.get('test_date', 'N/A')}

h2. Summary

Automated testing detected *{total_errors} errors* across *{len(categorized)} categories* during navigation testing. These are filtered errors that do not block functionality but indicate underlying issues that should be addressed.

h2. Test Context

* *Test Name:* {test_context.get('test_name', 'N/A')}
* *Test URL:* {test_context.get('test_url', 'https://www.toyota.com')}
* *Browser:* {test_context.get('browser', 'Chromium')}
* *Platform:* {test_context.get('platform', 'macOS')}
* *Date:* {test_context.get('test_date', 'N/A')}

===========================================================

"""

        # Add each category as a section
        issue_num = 1
        for category, errors in categorized.items():
            if not errors:
                continue

            ticket += f"h2. Issue #{issue_num}: "

            # Category-specific headers
            if category == 'video_playback':
                ticket += f"Video Autoplay Errors ({len(errors)} occurrences)\n\n"
                ticket += "*Priority:* Low-Medium\n*Component:* Frontend / Media Player\n\n"
                ticket += "h3. Description\n\nVideo autoplay race condition causing Promise rejections.\n\n"
                ticket += "*Error Message:*\n{code:javascript}\n"
                ticket += f"{errors[0].get('message', 'N/A')}\n"
                ticket += "{code}\n\n"
                ticket += "h3. Steps to Reproduce\n\n"
                ticket += "# Open Chrome DevTools → Console tab\n"
                ticket += "# Navigate to: https://www.toyota.com/camry\n"
                ticket += "# Observe video playback errors during page load\n"
                ticket += "# Navigate to #gallery and #features sections\n\n"
                ticket += "h3. Expected vs Actual Behavior\n\n"
                ticket += "*Expected:*\n"
                ticket += "* Videos should autoplay without console errors\n"
                ticket += "* play() Promise should resolve successfully\n"
                ticket += "* No race conditions between play() and pause() calls\n\n"
                ticket += "*Actual:*\n"
                ticket += f"* {len(errors)} video playback errors detected\n"
                ticket += "* play() Promise interrupted by pause() calls\n"
                ticket += "* Race condition occurs during page load and navigation\n\n"
                ticket += f"h3. Impact\n\n* Severity: Low-Medium\n* User Impact: Videos still work, console errors present\n* Occurrences: {len(errors)}\n\n"

            elif category == 'dealer_lookup':
                ticket += f"Dealer API Failures ({len(errors)} occurrences)\n\n"
                ticket += "*Priority:* Medium\n*Component:* Backend API / Dealer Services\n\n"
                ticket += "h3. Description\n\nDealer lookup API failing for specific dealer codes.\n\n"
                ticket += "*Error Message:*\n{code:javascript}\n"
                ticket += f"{errors[0].get('message', 'N/A')}\n"
                ticket += "{code}\n\n"
                ticket += "h3. Steps to Reproduce\n\n"
                ticket += "# Open Chrome DevTools → Console tab\n"
                ticket += "# Navigate to: https://www.toyota.com\n"
                ticket += "# Wait for page load\n"
                ticket += "# Observe dealer lookup errors\n\n"
                ticket += "h3. Expected vs Actual Behavior\n\n"
                ticket += "*Expected:*\n"
                ticket += "* Dealer API should return valid dealer information\n"
                ticket += "* No console errors related to dealer lookups\n"
                ticket += "* All dealer codes should be valid and accessible\n\n"
                ticket += "*Actual:*\n"
                ticket += f"* {len(errors)} dealer lookup errors detected\n"
                # Extract unique dealer codes from errors
                dealer_codes = set()
                for err in errors:
                    msg = err.get('message', '')
                    if '12166' in msg:
                        dealer_codes.add('12166')
                    if '12161' in msg:
                        dealer_codes.add('12161')
                if dealer_codes:
                    ticket += f"* Failing dealer codes: {', '.join(dealer_codes)}\n"
                else:
                    ticket += "* Dealer API returning errors\n"
                ticket += "* Users may not see their local dealer\n\n"
                ticket += f"h3. Impact\n\n* Severity: Medium\n* User Impact: Users may not see local dealer information\n* Occurrences: {len(errors)}\n\n"

            elif category == 'js_undefined':
                ticket += f"JavaScript Undefined Errors ({len(errors)} occurrences)\n\n"
                ticket += "*Priority:* Medium\n*Component:* Frontend / JavaScript\n\n"
                ticket += "h3. Description\n\nJavaScript attempting to access properties on undefined objects.\n\n"
                ticket += "*Error Messages:*\n{code:javascript}\n"
                for i, err in enumerate(set(e.get('message', '') for e in errors[:3])):
                    ticket += f"{err}\n"
                ticket += "{code}\n\n"
                ticket += "h3. Steps to Reproduce\n\n"
                ticket += "# Open Chrome DevTools → Console tab\n"
                ticket += "# Navigate to: https://www.toyota.com\n"
                ticket += "# Click Vehicles → RAV4\n"
                ticket += "# Observe JavaScript errors during page load\n\n"
                ticket += "h3. Expected vs Actual Behavior\n\n"
                ticket += "*Expected:*\n"
                ticket += "* No JavaScript errors during page interactions\n"
                ticket += "* All object properties should be checked before access\n"
                ticket += "* Proper null/undefined handling throughout code\n\n"
                ticket += "*Actual:*\n"
                ticket += f"* {len(errors)} JavaScript undefined errors detected\n"
                # Extract unique error types
                unique_errors = set(e.get('message', '') for e in errors)
                for err_msg in list(unique_errors)[:3]:
                    if 'Cannot read properties of undefined' in err_msg:
                        # Extract the property being accessed
                        if 'reading' in err_msg:
                            ticket += f"* Attempting to access properties on undefined object\n"
                            break
                ticket += "* Missing null checks before property access\n"
                ticket += "* Potential for UI glitches or broken functionality\n\n"
                ticket += f"h3. Impact\n\n* Severity: Medium\n* User Impact: Potential UI glitches, memory leaks\n* Occurrences: {len(errors)}\n\n"

            elif category == 'network_503':
                ticket += f"Third-Party Service Failures ({len(errors)} occurrences)\n\n"
                ticket += "*Priority:* Low\n*Component:* Third-Party Integrations / Advertising\n\n"
                ticket += "h3. Description\n\nThird-party advertising pixels returning HTTP 503 errors.\n\n"
                ticket += "*Failed Services:*\n"
                for url in set(e.get('details', {}).get('url', 'unknown') for e in errors[:3]):
                    ticket += f"* {url[:80]}...\n"
                ticket += "\n"
                ticket += "h3. Steps to Reproduce\n\n"
                ticket += "# Open Chrome DevTools → Network tab\n"
                ticket += "# Filter by: d.agkn.com\n"
                ticket += "# Navigate to: https://www.toyota.com\n"
                ticket += "# Observe 503 errors in network panel\n\n"
                ticket += "h3. Expected vs Actual Behavior\n\n"
                ticket += "*Expected:*\n"
                ticket += "* All third-party tracking pixels should load successfully\n"
                ticket += "* HTTP 200 responses from advertising services\n"
                ticket += "* Complete tracking and analytics data capture\n\n"
                ticket += "*Actual:*\n"
                ticket += f"* {len(errors)} HTTP 503 errors from third-party services\n"
                # Extract unique domains
                unique_domains = set()
                for err in errors:
                    url = err.get('details', {}).get('url', '')
                    if 'd.agkn.com' in url:
                        unique_domains.add('d.agkn.com (advertising pixel)')
                if unique_domains:
                    ticket += f"* Failing services: {', '.join(unique_domains)}\n"
                ticket += "* Incomplete analytics/tracking data\n"
                ticket += "* Service unavailable intermittently\n\n"
                ticket += f"h3. Impact\n\n* Severity: Low\n* User Impact: None - page works normally\n* Business Impact: Incomplete tracking data\n* Occurrences: {len(errors)}\n\n"

            else:
                # Handle "other" category with full documentation
                ticket += f"{category.replace('_', ' ').title()} ({len(errors)} occurrences)\n\n"
                ticket += "*Priority:* Medium\n*Component:* Frontend / JavaScript / Tracking\n\n"
                ticket += "h3. Description\n\n"
                ticket += "Multiple console errors detected that don't fit standard categories. These include:\n\n"

                # Group unique error messages
                unique_messages = {}
                for err in errors:
                    msg = err.get('message', 'Unknown')
                    if msg not in unique_messages:
                        unique_messages[msg] = 0
                    unique_messages[msg] += 1

                ticket += "*Error Types:*\n"
                for msg, count in unique_messages.items():
                    ticket += f"* {msg} ({count} occurrence{'s' if count > 1 else ''})\n"
                ticket += "\n"

                ticket += "*Sample Error Messages:*\n{code:javascript}\n"
                for msg in list(unique_messages.keys())[:3]:
                    ticket += f"{msg}\n"
                ticket += "{code}\n\n"

                ticket += "h3. Steps to Reproduce\n\n"
                ticket += "# Open Chrome DevTools → Console tab\n"
                ticket += "# Clear console (trash icon)\n"
                page_url = errors[0].get('page_url', 'https://www.toyota.com')
                ticket += f"# Navigate to: {page_url}\n"
                ticket += "# Observe console errors during page load\n"
                ticket += "# Check for errors related to undefined variables or missing tracking IDs\n\n"

                ticket += "h3. Expected vs Actual Behavior\n\n"
                ticket += "*Expected:*\n"
                ticket += "* No console errors during page load\n"
                ticket += "* All JavaScript variables properly initialized\n"
                ticket += "* Tracking IDs present when required\n\n"
                ticket += "*Actual:*\n"
                ticket += f"* {len(errors)} console errors detected\n"
                for msg, count in unique_messages.items():
                    ticket += f"* {count}x: {msg}\n"
                ticket += "\n"

                ticket += "h3. Technical Details\n\n"
                ticket += f"* *First Occurrence:* {errors[0].get('timestamp', 'N/A')}\n"
                ticket += f"* *Affected Pages:* {', '.join(set(e.get('page_url', 'unknown') for e in errors))}\n"
                ticket += f"* *Total Occurrences:* {len(errors)}\n\n"

                ticket += "h3. Impact Assessment\n\n"
                ticket += "* *Severity:* Medium\n"
                ticket += "* *User Impact:* Minimal - page functionality appears normal\n"
                ticket += "* *Technical Impact:* Console pollution, potential memory leaks, debugging difficulty\n"
                ticket += "* *Business Impact:* May affect analytics tracking accuracy\n"
                ticket += f"* *Frequency:* {len(errors)} occurrences detected during testing\n\n"

                ticket += "h3. Root Cause Analysis\n\n"
                ticket += "*Possible Causes:*\n"
                ticket += "* Missing null/undefined checks in JavaScript code\n"
                ticket += "* Tracking IDs not properly initialized\n"
                ticket += "* Race conditions in script loading order\n"
                ticket += "* Third-party script integration issues\n\n"

                ticket += "h3. Recommended Actions\n\n"
                ticket += "# Review JavaScript code for undefined variable access\n"
                ticket += "# Add defensive null checks before accessing object properties\n"
                ticket += "# Verify tracking ID initialization in analytics scripts\n"
                ticket += "# Add error handling for missing required values\n"
                ticket += "# Test across different page load scenarios\n\n"

                ticket += "h3. Suggested Fix\n\n"
                ticket += "{code:javascript}\n"
                ticket += "// Before - unsafe access\n"
                ticket += "const value = someObject.property;\n\n"
                ticket += "// After - safe access with null checks\n"
                ticket += "const value = someObject?.property ?? defaultValue;\n\n"
                ticket += "// For tracking IDs\n"
                ticket += "if (typeof dgid !== 'undefined' && dgid !== null) {\n"
                ticket += "  // Use dgid\n"
                ticket += "} else {\n"
                ticket += "  console.warn('dgid not available');\n"
                ticket += "}\n"
                ticket += "{code}\n\n"

            ticket += "\n===========================================================\n\n"
            issue_num += 1

        # Add recommendations section
        ticket += """h2. Overall Recommendations

# *Video Playback*: Add proper error handling for autoplay Promises
# *Dealer API*: Verify dealer codes exist, add fallback behavior
# *JavaScript Errors*: Add null checks before accessing object properties
# *Network Errors*: Review third-party service reliability

h2. Test Evidence

*Automated Test Run:* {test_name}
*Total Errors Detected:* {total_errors}
*Error Categories:* {num_categories}
*All Errors Filtered:* Tests still pass - these are website bugs, not test failures

h2. Notes

* These errors were automatically detected during E2E testing
* All functionality tested works correctly despite these errors
* Tests use AI-powered anomaly detection to capture console/network errors
* Errors are filtered so tests pass (focus on functionality, not website bugs)
* This report helps track technical debt and improve website quality

h2. Attachments

For detailed error information, see:
* JSON Report: Full error details with timestamps
* Test Logs: Complete test execution logs
""".format(
            test_name=test_context.get('test_name', 'N/A'),
            total_errors=total_errors,
            num_categories=len(categorized)
        )

        return ticket

    def generate_report(
        self,
        anomalies: List,
        test_name: str,
        test_url: str = "https://www.toyota.com",
        browser: str = "Chromium",
        platform: str = "macOS"
    ) -> Dict[str, Any]:
        """
        Generate complete error report with JSON export and JIRA tickets.

        Args:
            anomalies: List of Anomaly objects from AnomalyDetector
            test_name: Name of the test that generated errors
            test_url: URL being tested
            browser: Browser used for testing
            platform: Platform/OS used for testing

        Returns:
            Dictionary containing report summary
        """
        timestamp = datetime.now()
        categorized = self.categorize_errors(anomalies)

        # Build test context
        test_context = {
            'test_name': test_name,
            'test_date': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'test_url': test_url,
            'browser': browser,
            'platform': platform
        }

        # Generate JSON report
        json_report = {
            'report_generated': timestamp.isoformat(),
            'test_context': test_context,
            'summary': {
                'total_errors': len(anomalies),
                'categories': {cat: len(errors) for cat, errors in categorized.items()}
            },
            'errors_by_category': categorized
        }

        # Save JSON report
        json_filename = f"error_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        json_path = self.report_dir / json_filename
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)

        print(f"\n📊 JSON Report saved: {json_path}")

        # Generate ONE consolidated JIRA ticket with all issues
        jira_dir = self.report_dir / "jira_tickets"
        jira_dir.mkdir(exist_ok=True)

        # Generate consolidated ticket with all error categories
        jira_content = self.generate_consolidated_jira_ticket(categorized, test_context)

        # Save consolidated JIRA ticket
        ticket_filename = f"JIRA_consolidated_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        ticket_path = jira_dir / ticket_filename
        with open(ticket_path, 'w') as f:
            f.write(jira_content)

        print(f"🎫 JIRA Ticket created: {ticket_path}")

        # Generate summary report
        summary_path = self.report_dir / f"SUMMARY_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        self._generate_summary(json_report, ticket_path, summary_path)
        print(f"📄 Summary Report: {summary_path}")

        return {
            'json_report': str(json_path),
            'jira_ticket': str(ticket_path),
            'summary': str(summary_path),
            'total_errors': len(anomalies),
            'categories': list(categorized.keys())
        }

    def _generate_summary(self, json_report: Dict, jira_ticket_path: Path, output_path: Path):
        """Generate human-readable summary report."""
        summary = f"""
================================================================================
FILTERED ERROR REPORT SUMMARY
================================================================================

Generated: {json_report['report_generated']}
Test: {json_report['test_context']['test_name']}
URL: {json_report['test_context']['test_url']}

TOTAL ERRORS DETECTED: {json_report['summary']['total_errors']}

ERROR BREAKDOWN BY CATEGORY:
{''.join(f"  • {cat}: {count} errors" + chr(10) for cat, count in json_report['summary']['categories'].items())}

CONSOLIDATED JIRA TICKET GENERATED:
  • All Issues: {jira_ticket_path}

================================================================================
NEXT STEPS:
================================================================================

1. Review the JSON report for detailed error information
2. Open the consolidated JIRA ticket and copy/paste content into your JIRA system
3. All error categories are organized as separate issues within one ticket
4. Assign appropriate priority and team members
5. Track error trends over time by comparing with previous reports

All reports saved to: {self.report_dir}

================================================================================
"""
        with open(output_path, 'w') as f:
            f.write(summary)
