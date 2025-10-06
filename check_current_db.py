import sqlite3

def check_database_status():
    try:
        conn = sqlite3.connect('assets.db')
        cursor = conn.cursor()
        
        # Get total assets
        cursor.execute('SELECT COUNT(*) FROM assets_enhanced')
        total_assets = cursor.fetchone()[0]
        print(f"🔍 TOTAL ASSETS IN DATABASE: {total_assets}")
        
        # Get column information
        cursor.execute('PRAGMA table_info(assets_enhanced)')
        columns = cursor.fetchall()
        print(f"🔍 TOTAL COLUMNS: {len(columns)}")
        
        # Get sample asset data
        cursor.execute('SELECT * FROM assets_enhanced WHERE id = 1')
        row = cursor.fetchone()
        
        if row:
            column_names = [desc[0] for desc in cursor.description]
            print("\n📊 SAMPLE ASSET DATA (First 30 fields):")
            for i in range(min(30, len(column_names))):
                value = row[i] if row[i] is not None else "None"
                print(f"{i:3d}. {column_names[i]:30} = {value}")
                
            print(f"\n... and {len(column_names)-30} more columns")
            
            # Check data completeness
            filled_columns = sum(1 for val in row if val is not None and val != "")
            completeness = (filled_columns / len(column_names)) * 100
            print(f"\n📈 DATA COMPLETENESS: {completeness:.1f}% ({filled_columns}/{len(column_names)} columns filled)")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        return False

if __name__ == "__main__":
    check_database_status()