# Visual Testing Options - See Tests Run with Your Own Eyes

## Option 1: Headed Mode (See Browser Window)

**Run any test with visible browser:**
```bash
pytest tests/recorded/test_gnav_clean.py --headed
```

**What you see:**
- ✅ Browser window opens
- ✅ All clicks, navigation, form fills visible
- ✅ Test runs at normal speed
- ✅ Browser closes when done

## Option 2: Slow Motion (See Actions Clearly)

**Slow down test execution by 500ms per action:**
```bash
pytest tests/recorded/test_gnav_clean.py --headed --slowmo 500
```

**What you see:**
- ✅ Browser window opens
- ✅ Each action pauses 500ms
- ✅ Perfect for watching what's happening
- ✅ Great for demos

**Adjust speed:**
```bash
--slowmo 100   # Fast (100ms pause)
--slowmo 500   # Medium (500ms pause)
--slowmo 1000  # Slow (1 second pause)
--slowmo 2000  # Very slow (2 second pause)
```

## Option 3: Debug Mode with Inspector

**Step through test line-by-line:**
```bash
PWDEBUG=1 pytest tests/recorded/test_gnav_clean.py -s
```

**What you see:**
- ✅ Browser window opens
- ✅ Playwright Inspector window opens
- ✅ Test PAUSES at each step
- ✅ You click "Step Over" to advance
- ✅ See highlighted elements as they're found
- ✅ Console shows all locators

**Inspector Features:**
- 🔍 Hover over code to see elements highlighted
- ⏯️ Step through actions one at a time
- 📸 Inspect element locators
- 🐛 Debug why tests fail

## Option 4: Video Recording (Watch Later)

**Record video of test execution:**
```bash
pytest tests/recorded/test_gnav_clean.py --video on
```

**Result:**
- Video saved to: `test-results/`
- Only records on **failure** by default
- Watch the entire test execution

**Record all tests (pass or fail):**
```bash
pytest tests/recorded/test_gnav_clean.py --video retain-on-failure
```

## Option 5: Screenshots on Failure

**Automatically capture screenshots when tests fail:**
```bash
pytest tests/recorded/test_gnav_clean.py --screenshot only-on-failure
```

**Screenshots saved to:** `test-results/`

## Quick Reference Commands

### See GNAV Test Run:
```bash
# Fast visual
pytest tests/recorded/test_gnav_clean.py --headed

# Slow motion (great for watching)
pytest tests/recorded/test_gnav_clean.py --headed --slowmo 1000

# Debug step-by-step
PWDEBUG=1 pytest tests/recorded/test_gnav_clean.py::test_gnav_all_vehicle_categories -s
```

### See Dealers Test Run:
```bash
# Fast visual
pytest tests/recorded/test_dealers_search_clean.py --headed

# Slow motion
pytest tests/recorded/test_dealers_search_clean.py --headed --slowmo 1000
```

### See ALL Tests Run:
```bash
# All tests in headed mode
pytest tests/recorded/ --headed

# All tests slow motion
pytest tests/recorded/ --headed --slowmo 500
```

## Advanced: Custom Viewport Size

**Run tests in specific window size:**
```bash
pytest tests/recorded/test_gnav_clean.py --headed --viewport-size=1920,1080
```

**Common sizes:**
- Desktop: `--viewport-size=1920,1080`
- Laptop: `--viewport-size=1366,768`
- Tablet: `--viewport-size=768,1024`
- Mobile: `--viewport-size=375,667`

## Pro Tips

### Watch Specific Test
```bash
# Watch just the GNAV categories test
pytest tests/recorded/test_gnav_clean.py::test_gnav_all_vehicle_categories --headed --slowmo 500
```

### Debug Failed Test
```bash
# When a test fails, debug it step-by-step
PWDEBUG=1 pytest tests/recorded/test_gnav.py::test_gnav_vehicles_menu_complete_flow -s
```

### Demo Mode (For Presentations)
```bash
# Perfect speed for showing stakeholders
pytest tests/recorded/test_gnav_clean.py --headed --slowmo 800 -v
```

### Record Everything
```bash
# Record video of all tests
pytest tests/recorded/ --headed --video on --screenshot on
```

## Troubleshooting

**Q: Browser opens too fast, can't see anything**
```bash
# Increase slow motion
pytest tests/recorded/test_gnav_clean.py --headed --slowmo 2000
```

**Q: Want to pause and inspect**
```bash
# Use debug mode
PWDEBUG=1 pytest tests/recorded/test_gnav_clean.py -s
```

**Q: Browser closes before I can see result**
```bash
# Add a wait at the end of test, or use debug mode
PWDEBUG=1 pytest tests/recorded/test_gnav_clean.py -s
```

**Q: Want to see in different browser**
```bash
# Firefox
pytest tests/recorded/test_gnav_clean.py --headed --browser firefox

# WebKit (Safari-like)
pytest tests/recorded/test_gnav_clean.py --headed --browser webkit
```
