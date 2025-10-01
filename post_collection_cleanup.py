
# Add this to your collection modules to automatically run cleanup
from integrated_duplicate_cleanup import IntegratedDuplicateCleanup

def run_post_collection_cleanup():
    """Run automatic cleanup after data collection"""
    cleanup = IntegratedDuplicateCleanup()
    cleanup.run_quick_cleanup()
    cleanup.verify_cleanup()
    
# Call this function after each collection session
