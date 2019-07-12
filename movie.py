from moviepy.editor import *
import scipy
import fileinput
from collections import defaultdict
import itertools
import ast
import datetime
import time
import os
from os import path
import speech_recognition as sr
import pprint
from operator import itemgetter
import psutil
import win32file
from more_itertools import unique_everseen

#print win32file._getmaxstdio()
#win32file._setmaxstdio(2048)

IBM_USR = #get credentials from IBM
IBM_PAS = #get credentials from IBM

def getTime(str):
	t = time.strptime(str.split(',')[0],'%H:%M:%S')
	return datetime.timedelta(hours=t.tm_hour,minutes=t.tm_min,seconds=t.tm_sec).total_seconds()

def rmvtype(str):
	size = len(str)
	return str[0:size-4]

def getMovie(subfile, movies):
	for i in movies:
		if rmvtype(subfile) == rmvtype(i):
			return i

def getData(line):
	data = ast.literal_eval(line)
	ngram = str(data[0])
	srt = str(data[1][0]).strip()
	stamp = str(data[1][1]).strip()

	return [ngram, srt, stamp]

def audioClip(srt, stamp, files):
	ts = stamp.split(' --> ')
	start = getTime(ts[0])
	end = getTime(ts[1])
	film = 'mymovies/'+getMovie(srt, files)

	return AudioFileClip(film).subclip(start - 2, end + 2)

def writeClips(clip_list, video_num):
	final = concatenate(clip_list)
	vid_name = "Final/clip_"+str(video_num)+'.mp4'
	final.write_videofile(vid_name, fps=24, codec='mpeg4', bitrate='2000k')

def finalWrite(video_num):
	clips = ['Final/clip_'+str(i)+'.mp4' for i in range(video_num)]

	group = []
	for clip in clips:
		group.append(VideoFileClip(clip))

	#group = [VideoFileClip(clip) for clip in clips]

	final = concatenate(group)
	final.write_videofile('Final/final_vid.mp4', fps=24, codec='mpeg4', bitrate='2000k')

def listen(clip, keys):
	voice = sr.Recognizer()
	audio_name = 'TEMPsound.wav'
	clip.write_audiofile(audio_name)
	#clip.audio.write_audiofile(audio_name)

	with sr.WavFile(audio_name) as source:
		audio = voice.record(source)
	a = voice.recognize_ibm(keys, audio, username=IBM_USR, password=IBM_PAS, show_all=True)
	#a = voice.recognize_ibm(keys, audio, username=IBM_USR, password=IBM_PAS, show_all=True)
	del audio
	return a

def keyWords(ngram):
	words = ast.literal_eval(ngram)
	return ' '.join(map(str.lower, words))

def formatKey(str):
	return str.replace(' ', ',')+','

def getKeyResults(json, keylength):
	'''
	look at results of IBM json key results
	extract key_results matching our tuple
	'''
	results = {}
	for i in range(len(json['results'])):
		size = len(set(json['results'][i]['keywords_result']))
		if size == keylength:
			results =  json['results'][i]['keywords_result']
	return results

def keyWordTimes(json):
	'''
	return time instance of key_word match after passing to IBM
	'''
	times = list()
	if len(json) > 0:
		for i in json:
			for j in json[i]:
				times.append([j['normalized_text'], j['start_time'], j['end_time']])
	return sorted(times, key=itemgetter(1))

def closestNeighbors(ngram, iterable):
	'''
	For a key_match of two or more, it is necessary to return only the words we want
	it so happens that our ordered pair of words, if found, occur chronologically and
	create a smallest area 'triangle' (start, end). Return these three words' timestamps
	'''
	obj = iterable
	ngram = map(str.lower,ast.literal_eval(ngram))
	keys = zip(*obj)[0]
	time = [obj[0][1], obj[len(keys)-1][2]]

	for i in range(len(keys) - len(ngram) + 1):
		if ngram[0] == keys[i].lower() and ngram[len(ngram)-1] == keys[i + len(ngram)-1].lower():
			return [obj[i][1], obj[i + len(ngram) - 1][2]]
	return time

def purgeProc(process):
	for proc in psutil.process_iter():
		if proc.name() == process:
			proc.kill()

def splitTime(stamp):
	ts = stamp.split(' --> ')
	start = getTime(ts[0])
	end = getTime(ts[1])
	return (start, end)

def checkMatch(a, b):
	a = map(str.lower,ast.literal_eval(a))
	b = list(unique_everseen(zip(*b)[0]))
	c = itertools.izip_longest(a, b)
	return all([x.lower() == y.lower() for (x,y) in c])

def makeClip(srt, start, end, files):
	film = 'mymovies/'+getMovie(srt, files)
	clip = VideoFileClip(film).subclip(start - 2, end - 2)
	vid = CompositeVideoClip([clip], size=(1280,720))
	return vid

def main():
	files = [f for f in os.listdir(path.relpath('mymovies/'))]

	instances = open('output.txt', 'r')

	video_num = 0
	clip_count = 0
	video = []

	PROCESS = 'ffmpeg.win32.exe'

	error = open('data.txt', 'w')
	found = ''
	line_count = 0
	for line in instances:
		data = getData(line)
		ngram = data[0]
		srt = data[1]
		timestamp = data[2]
		if clip_count < 20:

			if data[2][0].isdigit() and ngram != found:
				#clip = makeClip(ngram, srt, timestamp, files)
				clip = audioClip(srt, timestamp, files)
				keys = formatKey(keyWords(data[0]))
				c = listen(clip, keys)

				if len(c['results']) > 0:
					kr = getKeyResults(c, len(keyWords(data[0]).split()))

					if len(kr) > 0 and checkMatch(ngram, keyWordTimes(kr)):
						print 'Found', ngram, zip(*keyWordTimes(kr))[0], clip_count, line_count
						newTime = closestNeighbors(data[0], keyWordTimes(kr))
						print ngram, newTime
						found = ngram
						error.write("[{0}, {1}, {2}]\n".format(ngram, c, srt))
						#clip = clip.subclip(newTime[0],newTime[1])
						time_sec = splitTime(timestamp)
						clip = makeClip(srt, (newTime[0] + time_sec[0]), (newTime[1] + time_sec[0]), files)

						video.append(clip)
						clip_count += 1
				# else:
				# 	del clip
				# 	del c
		else:
			writeClips(video, video_num)
			purgeProc(PROCESS)
			clip_count = 0
			video_num+=1
			#del video[:]
			#time.sleep(20)
		line_count += 1

	writeClips(video, video_num)
	video_num+=1
	finalWrite(video_num)

main()