import pandas as pd

#Extract the songs from the train dataset 
def main():
    # Load the music_mood.csv file
    music_mood_df = pd.read_csv("C:/Users/pc/Documents/Statistical Learning/Task 2 A Noviilo/spotify-2023.csv",encoding='latin-1')
    
    # Extract the Artists and Name arrays
    artists = music_mood_df['artist(s)_name']
    songs = music_mood_df['track_name']
    # Create the DataFrame for scrapeSongs.csv
    key = music_mood_df["key"]
    mode = music_mood_df["mode"].replace({"Major": "", "Minor": "m"})
    data = {
        "Artists": artists,
        "Name": songs,
        "Key": key + mode
    }
    df = pd.DataFrame(data)
    
    # Save the DataFrame to CSV
    df.to_csv("data/scrapeSongs.csv", index=False)

if __name__ == "__main__":
    main()
