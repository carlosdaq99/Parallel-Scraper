# Browser Pool Configuration Fix - Permanent Setting
# Run this to permanently set the browser pool size to 1

$env:OPT_BROWSER_POOL_SIZE = "1"

# Verify the setting
python -c "import os; print('OPT_BROWSER_POOL_SIZE:', os.getenv('OPT_BROWSER_POOL_SIZE', 'NOT_SET'))"
python -c "from config import OptimizationConfig; print('Config BROWSER_POOL_SIZE:', OptimizationConfig.BROWSER_POOL_SIZE)"
python -c "from optimization_utils import OptimizationConfig; print('Optimization Utils BROWSER_POOL_SIZE:', OptimizationConfig.BROWSER_POOL_SIZE)"
