import duckdb
import boto3
import os

# Used to check the class work with tennis data in S3
class TennisS3Data:
    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.db = duckdb.connect()
        
        # Set up DuckDB to read from S3
        self.db.execute("INSTALL httpfs")
        self.db.execute("LOAD httpfs")
        
        # Set AWS credentials for DuckDB
        # Get credentials from your AWS CLI config
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials:
            self.db.execute(f"SET s3_region='us-east-1'")
            self.db.execute(f"SET s3_access_key_id='{credentials.access_key}'")
            self.db.execute(f"SET s3_secret_access_key='{credentials.secret_key}'")
            print("AWS credentials configured for DuckDB")
        else:
            print("No AWS credentials found")
    
    def load_tennis_data(self):
        # Load data directly from S3
        s3_path = f"s3://{self.bucket}/data/atp_tennis.csv"
        query = f"CREATE TABLE matches AS SELECT * FROM read_csv_auto('{s3_path}')"
        self.db.execute(query)
        print("Data loaded from S3")
    
    def get_basic_stats(self):
        # Get simple statistics
        query = """
        SELECT 
            COUNT(*) as total_matches,
            Surface,
            COUNT(*) as surface_count
        FROM matches 
        WHERE Rank_1 > 0 AND Rank_2 > 0
        GROUP BY Surface
        """
        return self.db.execute(query).fetchdf()
    
    def get_top_players(self):
        # Find most active players
        query = """
        SELECT Player_1 as player, COUNT(*) as matches
        FROM matches 
        WHERE Rank_1 <= 50
        GROUP BY Player_1
        ORDER BY matches DESC
        LIMIT 10
        """
        return self.db.execute(query).fetchdf()

# Test it
if __name__ == "__main__":
    tennis = TennisS3Data("tennis-cfu-2024")
    tennis.load_tennis_data()
    
    print("Basic Stats:")
    print(tennis.get_basic_stats())
    
    print("Top Players:")
    print(tennis.get_top_players())
