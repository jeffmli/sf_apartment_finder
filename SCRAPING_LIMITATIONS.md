# Web Scraping Limitations & Workarounds

This document explains the challenges with scraping apartment websites and provides practical solutions.

## Understanding 403 Forbidden Errors

### What is a 403 Error?

When you see this in your logs:
```
ERROR - Network error scraping Zillow: 403 Client Error: Forbidden
```

This means the website is **actively blocking** automated access. The server recognized your request as a bot and refused to serve the page.

### Why It Happens

Modern real estate websites use sophisticated anti-bot protection:

1. **Browser Fingerprinting**: Detecting missing JavaScript execution, canvas rendering, etc.
2. **IP Reputation**: Tracking request patterns from your IP address
3. **Rate Limiting**: Too many requests in a short time
4. **User Agent Analysis**: Identifying scrapers by headers
5. **CAPTCHA Challenges**: Requiring human interaction
6. **Cookies and Sessions**: Expecting browser-like session management

## Site-by-Site Analysis

### Craigslist ✅ (Recommended)

**Status**: **Usually works reliably**

**Why it works:**
- Less aggressive anti-bot measures
- More scraper-tolerant Terms of Service
- Simpler HTML structure
- No JavaScript rendering required

**Recommendation**: **Keep this enabled** - it's your most reliable source

**Typical results**: 20-50 listings per search

### Zillow ⚠️ (Often Blocked)

**Status**: **Frequently returns 403 errors**

**Why it's blocked:**
- Heavy JavaScript rendering (React-based SPA)
- Sophisticated bot detection (PerimeterX/DataDome)
- Requires browser-like fingerprints
- Sessions tracked across requests

**Workarounds:**
1. **Disable in config** (recommended)
2. Use their official API (requires partnership)
3. Use Selenium with headless Chrome (slower, still may be blocked)
4. Manually browse Zillow separately

**Recommendation**: **Disable this scraper** unless you're getting consistent results

### Apartments.com ⚠️ (Often Blocked)

**Status**: **Frequently returns 403 errors**

**Why it's blocked:**
- CloudFlare bot protection
- JavaScript challenges
- Cookie/session requirements
- IP-based rate limiting

**Workarounds:**
1. **Disable in config** (recommended)
2. Use third-party APIs (like RapidAPI)
3. Use Selenium with headless Chrome
4. Manually browse Apartments.com separately

**Recommendation**: **Disable this scraper** unless you're getting consistent results

## Current Implementation

### What We've Already Done

The scraper includes several anti-detection measures:

✅ **Rotating User Agents**: Uses 7 different browser fingerprints
✅ **Realistic Headers**: Includes Sec-Fetch headers, Accept-Language, etc.
✅ **Delays Between Requests**: 3-5 second delays
✅ **Exponential Backoff**: Retries with increasing delays
✅ **Google Referer**: Makes requests appear to come from search
✅ **Session Management**: Maintains cookies across requests

### Why It Still Gets Blocked

Even with these measures, Zillow and Apartments.com can still block requests because:
- They detect the absence of JavaScript execution
- No mouse movements or scrolling
- Missing WebGL/Canvas fingerprints
- No browser automation framework signatures
- IP reputation from previous scraping attempts

## Recommended Configuration

### For Best Results

Edit your `config.yaml`:

```yaml
scrapers:
  craigslist:
    enabled: true    # ✅ Keep enabled - works well

  zillow:
    enabled: false   # ❌ Disable - frequently blocked

  apartments_com:
    enabled: false   # ❌ Disable - frequently blocked
```

### Why This Works

- **Craigslist alone** usually provides 20-50 listings per search
- You avoid the frustration of 403 errors
- Faster execution (no waiting for blocked requests)
- More reliable daily emails
- Lower chance of IP blocks

## Alternative Approaches

If you need more than just Craigslist:

### 1. Manual Browsing (Easiest)

Set up saved searches on Zillow and Apartments.com:
- Save your search criteria
- Enable email alerts
- They'll send you daily updates
- 100% legal and reliable

### 2. Selenium with Headless Chrome (Advanced)

Requires updating the scrapers to use Selenium:

**Pros:**
- Executes JavaScript like a real browser
- Better success rate
- Can handle CAPTCHAs with services

**Cons:**
- Much slower (10-30 seconds per page)
- Requires Chrome/ChromeDriver installation
- Higher memory usage
- Still may be blocked

**Installation:**
```bash
pip install selenium webdriver-manager
```

### 3. Official APIs (Professional)

Some sites offer official APIs:

**Zillow**: Bridge Interactive (requires partnership)
**RapidAPI**: Various apartment listing APIs (paid)

**Pros:**
- Legal and reliable
- No blocking
- Clean data
- Supported

**Cons:**
- Usually paid
- May have usage limits
- Requires API keys

### 4. Third-Party Services

Consider services like:
- **Rentometer**: Rental market data API
- **Zillow API** (if you qualify)
- **Rental Beast**: Multi-source aggregation
- **PadMapper**: Aggregates from multiple sources

## Legal & Ethical Considerations

### Is Web Scraping Legal?

**Short answer**: It's complicated

**General guidelines:**
1. **Personal use**: Generally more acceptable
2. **Commercial use**: Often violates ToS
3. **Public data**: More defensible
4. **Rate limiting**: Be respectful
5. **Terms of Service**: May prohibit scraping

### Best Practices

✅ **DO:**
- Use reasonable delays between requests
- Respect robots.txt
- Use for personal apartment hunting
- Stop if asked (via ToS or cease-and-desist)
- Disable scrapers that are blocked

❌ **DON'T:**
- Make excessive requests
- Ignore ToS violations
- Use for commercial purposes
- Republish scraped data
- Try to evade blocks aggressively

## Troubleshooting

### If Craigslist Gets Blocked

This is rare, but if it happens:

1. **Increase delays**: Edit `request_handler.py`
   ```python
   self.request_handler = SmartRequestHandler(base_delay=10.0)
   ```

2. **Reduce max results**: Edit `config.yaml`
   ```yaml
   max_results_per_site: 20
   ```

3. **Check your IP**: You may be on a shared IP that's been flagged

4. **Wait 24 hours**: IP blocks are usually temporary

### If All Scrapers Fail

1. **Check internet connection**: `ping google.com`
2. **Check DNS**: `nslookup craigslist.org`
3. **Check firewalls**: VPN, corporate firewall, etc.
4. **Review logs**: `logs/scraper_YYYYMMDD.log`
5. **Test manually**: Try visiting sites in browser

## Future Improvements

Possible enhancements (not currently implemented):

1. **Residential Proxy Rotation**: Use proxy services
2. **Browser Automation**: Selenium/Playwright integration
3. **CAPTCHA Solving**: Services like 2Captcha
4. **Cloudflare Bypass**: cloudscraper library
5. **API Integration**: Official APIs where available

## Summary

**Bottom Line:**
- **Use Craigslist** - it works reliably
- **Disable Zillow and Apartments.com** - they block scrapers
- **Expect 20-50 listings per day** from Craigslist
- **Supplement with manual browsing** on other sites
- **Consider official email alerts** from Zillow/Apartments.com

This approach is:
- ✅ Legal and ethical
- ✅ Reliable and consistent
- ✅ Low-maintenance
- ✅ Respectful of website policies

Happy apartment hunting! 🏠
