# PowerShell script to run scraper with dashboard disabled
$env:SCRAPER_ENABLE_DASHBOARD='false'
python main_self_contained.py

# To re-enable dashboard
$env:SCRAPER_ENABLE_DASHBOARD='true'
python main_self_contained.py

# To use default (enabled)
Remove-Item Env:SCRAPER_ENABLE_DASHBOARD -ErrorAction SilentlyContinue
python main_self_contained.py
