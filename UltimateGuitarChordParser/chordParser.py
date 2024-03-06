

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import glob
import time

import chromedriver_autoinstaller
import re

extract_integer = lambda string: int(re.findall(r'\d+', string)[0])

"""
Parent function to scrape the chord progression of a single song from ultimate-guitar.com
    Parameters: 
     -wd = webdriver executable file (can use included chromedriver)
     - song: the name of the song you want to scrape
     - artist: name of the artist who the song is by
"""
def init_webpage(wd,song,artist,cookies = False):
    url = 'https://www.ultimate-guitar.com/explore?type[]=Chords'
    wd.get(url)
    time.sleep(2)
    if cookies:
        cookie = '/html/body/div[1]/div/div/div/div[2]/div/button[2]'
        wd.find_element(By.XPATH,cookie).click()
    #Search for the song name 
    searchBar =  wd.find_element(By.TAG_NAME,"input")
    searchBar.send_keys(artist+ " "+song)
    searchBar.send_keys(Keys.ENTER)
    time.sleep(2)
    return wd
def scrapeUltimateGuitar(wd, song, artist,key):
    init_webpage(wd,song,artist, cookies = True)
    
    #Search Chords only 
    try:
        chordsPath = "/html/body/div[1]/div[3]/main/div[2]/div[2]/section/nav/div[1]/nav/a[2]"
        chords = wd.find_element(By.XPATH,chordsPath)
        chords.click()
        time.sleep(2)
    except:
        print("There was no chords button")
    
    #Pick the top rated listing
    time.sleep(2)
    try:
        bestPath = "/html/body/div[1]/div[3]/main/div[2]/div[2]/section/article/div/div[4]/div[2]/header/span/span/a"
        highestRated = wd.find_element(By.XPATH,bestPath)
        highestRated.click()
        
        time.sleep(5)
        cookie2 = '/html/body/div[1]/div/div/div/div[2]/div/button[2]'
        wd.find_element(By.XPATH,cookie2).click()
        

        
               
        data = chordScraper(wd,key)
        if data == None:
            wd.execute_script("window.history.go(-1)")
            time.sleep(5)
            return None
        else:

            return data
     
        
    except:
        try:
            init_webpage(wd,song,artist)
            chordsPath = "/html/body/div[1]/div[3]/main/div[2]/div[2]/section/nav/div[1]/nav/a[2]"
            chords = wd.find_element(By.XPATH,chordsPath)
            chords.click()
            time.sleep(2)
            bestPath = "/html/body/div[1]/div[3]/main/div[2]/div[2]/section/article/div/div[3]/div[2]/header/span/span/a"
            highestRated = wd.find_element(By.XPATH,bestPath)
            highestRated.click()
            
            time.sleep(5)
            cookie2 = '/html/body/div[1]/div/div/div/div[2]/div/button[2]'
            wd.find_element(By.XPATH,cookie2).click()
            time.sleep(2)
            
      
            
        
            data = chordScraper(wd,key)
            if data == None:
                wd.execute_script("window.history.go(-1)")
                time.sleep(5)
                return None
            else:

                return data
         
            
        except:
            print("ERROR: OUT")
            

                
    
    
#Function to be run when you are on the webpage you want to scrape
# Will scrape the chord data of the song transposed to the key of C major
def chordScraper(wd,key):

    
    html = wd.page_source
    soup = BeautifulSoup(html, 'html.parser')
    time.sleep(2)
    #Get key data
    # FIX KEY
    print(key)
    
    capo = 0
    text_without_id = [span.text for td in soup.find_all('td', attrs ={'class':'IcoWj'}) for span in td.find_all('span') if not span.has_attr('id')]
    notes_pattern = ['A', "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab",'A', "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    for text in text_without_id:
        if any(note in text for note in notes_pattern):
            key = text  
            
        else:
            capo = 0 if text == 'no capo' else extract_integer(text)
            
    
    if key == "":
        if not key.isna():
            key = str(key).strip()
        else:
            return None
        
    print(f"Key: {key}, capo: {capo}")
    #standardize the key to C major
    wd = transposeToC(wd, key, capo)
    
    #Now should be in C major

    body = BeautifulSoup(wd.page_source, 'html.parser').find_all('span', attrs ={'class':'y68er'})
    body_text = [page.text for page in body]


    #Try to split into different song sections
    #secs = ["Intro", "Hook","Verse","Chorus","Pre-Chorus","Post-Chorus", "Bridge", "Interlude","Solo","Outro"]
    #regex = "\[(.*?)\]"
    #sections = re.split(regex,str(body_text))

    # Initialize an empty list to store the chords
    secChords = []

    # Flag to indicate whether the chorus section has been found
    found_chorus = False

    # Iterate through the lines of the lyrics
    for line in body_text:
        # Check if the line corresponds to the chorus section
        if re.search(r'\bChorus\b', line.strip()) and not re.search(r'\bPre-Chorus\b', line.strip()) :
            found_chorus = True
            print(found_chorus)
            continue  # Skip the line containing the section header
        # If the chorus section has been found and the line is not empty
        elif found_chorus:
            try:
                if line.strip().split()[0].startswith(('C', 'Cm', 'Dm', 'Ddim', 'Em', 'E#', 'F', 'Fm', 'G', 'Gm', 'Am', 'A#', 'Bdim', 'B#')):
                    # Extract the chord from the line and append it to the list
                    if len(line.strip().split()) <= 7:
                        secChords.extend(line.strip().split())
            except:
                pass
            if re.search(r'\bVerse\b', line.strip()):
                found_chorus = False
                break
    secChords = [chord for chord in secChords if chord != 'N.C.']        
    print(secChords)
    
    #Data will be held in a dictionary with the key being the section, and the value being a list of the progression,
    #   the end (this one will be None if the end is the same as the whole thing), number of chords in the section, 
    #   number of nondiatonic chords and number of extended chords 
    data = {} 
    secDataNext=True
    secLabel = "Intro"
   
    progression = []
    chords = []
    for c in range(len(secChords)):
        progression.append(secChords[c])
        if c == len(secChords)-1 and chords == []:
            chords = secChords
        #check if this is the point of circular nature in the chord progression
        elif len(progression) > 1 and progression[-1] == progression[0]:
            progLen = len(progression) -1 
            qualify = True
            for i in range(progLen):
                if len(secChords)-1 < progLen + i: 
                    #Then this is the progression
                    chords = secChords
                #check to see if this pattern repeats itself
                elif secChords[i] != secChords[progLen + i]:
                    qualify= False
                    break
            if qualify:
                chords = progression[:-1]
                print("Chords are : " + str(chords))
                break
    if chords == []:
        chords = progression
                
    #See if the end of the progression is different at all
    end = []
    i = len(chords) -1
    if secChords[-1] == chords[i]:
        if i == len(chords) -1 and i != 0 and secChords[-2] != chords[i-1]: 
            end = [secChords[-2] , secChords[-1]]
            counter1 = len(chords) - 3
            counter2 = -3
            while secChords[counter2] !=chords[counter1] and counter1 > 0:
                end = [secChords[counter2]]+ end
                counter1 -= 1
                counter2 -= 1
    else:
        end = [secChords[-1]]
        counter1 = len(chords) - 2
        counter2 = -1
        while secChords[counter2] != chords[counter1] and counter1 > 0:
            end = [secChords[counter2]] + end
            counter1 -= 1
            counter2 -= 1
    
    #count extended chords, do not consider the 5 extension, as it is just a part of regular major/minor chord 
    extendedChords = 0
    if end != []:
        for val in end:
            if not "5" in val and (''.join([i for i in val if i.isdigit()]) != "" or 'sus' in val or 'add' in val):
                extendedChords += 1
                val.replace("sus", "")
            elif '/' in val:
                extendedChords += 1

    for val in chords:
        if not "5" in val and (''.join([i for i in val if i.isdigit()]) != "" or 'sus' in val or 'add' in val):
            extendedChords += 1
            val.replace("sus", "")
        elif '/' in val:
            extendedChords += 1
    
    #Get number of non-diatonic chords and get the chord pattern in notation
    chords, outKey1 = diatonicPattern(chords)
    
    #do the same for the end pattern
    end, outKey2 = diatonicPattern(end)
    nonDiatonicChords = outKey1 + outKey2
    
    if end == "":
        end = None
    if secDataNext:
        data[secLabel]= [chords, end, len(set(secChords)), nonDiatonicChords, extendedChords]
        secDataNext = False
    if secLabel in list(data.keys()) and data[secLabel] == []:
        print("EMPTY SECTION")
        del data[secLabel]
    return data


#Returns the data on each section of each song in the scrapeSongs.csv file. 
# Will only get the data of artists in 'inputArtists'
def scrapeSongChords():
   

    scrapeSongs = pd.DataFrame(pd.read_csv("data/scrapeSongs.csv"))
    done = []
    df = pd.DataFrame(columns=['Name', 'Artist', 'Section', 'Progression', 'EndDifferent', 'NumSectionChords', 'nonDiatonicChords', 'extendedChords'])
    for index, row in scrapeSongs.iterrows():
        if (row["Name"], row['Artists'],row["Key"]) not in done:
            try:
                from selenium.webdriver.chrome.options import Options
                chrome_options = Options()
                chrome_options.add_argument("--disable-notifications")
                wd = webdriver.Chrome(options=chrome_options)
                data = scrapeUltimateGuitar(wd, row["Name"], row['Artists'],row["Key"])
                print(data)
            except:
                print("Diverted from site")
                done.append((row["Name"], row['Artists']))
                continue
            if data == None:
                done.append((row["Name"], row['Artists']))
                continue
            else:
                df = dictToDF(data,df,row["Name"], row['Artists'])
                done.append((row["Name"], row['Artists']))
                
    try:
        df.to_csv('data/songSections.csv')
    except:
        print("No valid tabs were found and there were no songs already saved, try searching for different songs!")


#Function to transpose the current chord sheet to the Key of C major
def transposeToC(driver, key, capo):
    majKeys = ['A', "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    transposeUp =  driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/main/div[2]/article[1]/div[1]/section[2]/article/section[5]/article/section/div[7]/div/span[2]/button[2]')
    transposeDown = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/main/div[2]/article[1]/div[1]/section[2]/article/section[5]/article/section/div[7]/div/span[2]/button[1]')

   
    #Check for if the key is flat, and then turn it to its corresponding sharp key
    if "b" in key:
        flatKeys = ['A', "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
        index = flatKeys.index(key[:2])
        newKey = majKeys[index]
        if "m" in key or "M" in key:
            key = newKey + 'm'
        else:
            key = newKey
            
    #if key is minor, make it its relative major key by transposing up 3 half steps
    if "m" in key or "M" in key:
        oldKey = key.replace('m', "")
        index = majKeys.index(oldKey)
        index = (index + 3)%12
        key = majKeys[index]

    #Now the chords should be in a major key
    
    #If the major key is C, then quit
    if key == 'C':
        return driver

    #Account for the capo if it is present, then transpose to C from the resulting key
    elif capo != 0:
        index = (majKeys.index(key) - capo)
        if index < 0: 
            key = majKeys[12 + index]
        else:
            key = majKeys[index]
    if key == 'C':
        return driver
    elif key in ["F#", "G", "G#", 'A', "A#", "B"]:
        while key != "C":
            index = (majKeys.index(key) + 1)%12
            time.sleep(2)
            transposeUp.click()
            key = majKeys[index]
    elif key in ["C#", "D", "D#", "E", "F"]:
        while key != "C":
            index = (majKeys.index(key) - 1)
            time.sleep(2)
            transposeDown.click()
            key = majKeys[index]
    time.sleep(5)
    return driver
        
    
#Lists out the detected chord progression of the section 
def diatonicPattern(chords):
    cMaj = ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]
    numerals = ["I", "ii", "iii", "IV", "V", "vi", "VII"]
    noExtend=[]
    nonDiatonic = 0
    
    for val in chords:
        if '/' in val:
            if 'm/' in val:
                val = val[0:2]
            else:
                val = val[0]
        noExtend.append(''.join([i for i in val if not i.isdigit()]).replace("maj", "").replace("sus", "").replace('dim', "").replace('aug', "").replace('(', "").replace(')', "").replace('add',""))

    numbers = ""
    last = ""
    prog = []
    for number in noExtend:
        if number != last:
            prog.append(number)
        last = number
    for c in prog:
        #Attempts to just get the numeral associated with a chord in the key of C major
        # If the current chord is not in cMaj, add the correct suffix
        try:
            numbers = numbers + "-" + numerals[cMaj.index(c)]
        except:
            cMajStripped = ["C", "D", "E", "F", "G", "A", "B"]
            nonDiatonic += 1
            suffix = ""
            if "#" in c:
                c = c.replace("#", "")
                suffix += "#"
            elif "b" in c:
                c = c.replace('b', "")
                suffix += "b"
            if 'dim' in c:
                c = c.replace('dim', "")
                suffix += ' dim'
            elif 'aug' in c:
                c = c.replace('aug', "")
                suffix += "aug"
            if 'm' in c:
                minor = True
                c = c.replace("m", "")
            elif "M" in c:
                minor = True
                c = c.replace("M", "")
            else:
                minor = False
            #need to handle a major where there should not be one or minor where there should not be one
            if minor: 
                numbers = numbers + "-"+ numerals[cMajStripped.index(c)].lower()+suffix
            else:
                numbers = numbers + "-"+ numerals[cMajStripped.index(c)].upper()+suffix
    return numbers[1:], nonDiatonic

#Function to turn dictionary key value pairs into dataframe rows
def dictToDF(data, df, song, artist):
    rows = []
    for key, value in data.items():
        if value == []:
            continue
        row = {'Name': song, 'Artist': artist, 'Section': key, 'Progression': value[0], 'EndDifferent': value[1], 'NumSectionChords': value[2], 'nonDiatonicChords': value[3], 'extendedChords': value[4]}
        rows.append(row)
    return pd.concat([df, pd.DataFrame(rows)], ignore_index=True)



def main():
    #inputArtists is the list of artists who show up in the the Artists column 
    # of 'scrapeSongs.csv' AND we want to actually scrape the songs of
    #music_mood_df = pd.read_csv("C:/Users/pc/Documents/Statistical Learning/Task 2 A Noviilo/imagine_dragons.csv")
    
    # Extract the Artists and Name arrays
    #inputArtists = music_mood_df['artist'] #all listed artists must be in scrapeSongs.csv
    scrapeSongChords()

if __name__ == "__main__":
    main()