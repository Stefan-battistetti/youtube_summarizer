from PIL import Image
import os
from stop_words import get_stop_words
import stylecloud
from youtube_transcript_api import YouTubeTranscriptApi
import openai
from keys import *

openai.api_key = OPENAI_API_KEY


def youtube_transcript(youtube_video="https://www.youtube.com/watch?v=zAtcRbYdvuw"):
    '''youtube transcripter, taking video's link and getting the text present in the video
    '''

    video_id = str(youtube_video).split("=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # getting the text from a list of dictionaries
    result = ""
    for i in transcript:
        result += ' ' + i['text']

    return result


def summarizer_api(result, tokens):
    """
        api to connect to gpt-3 and summarizer the text
    """

    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=result + "\nTl;dr",
        temperature=1,
        max_tokens=tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response


def sentiment_analyzer(summarized_text):
    """
        api to connect to gpt-3 and get the sentiment score of a text
    """

    sentiment_score = openai.Completion.create(
        engine="text-davinci-001",
        prompt="Classify the sentiment of this text in POSITIVE, NEUTRAL or NEGATIVE.\n\ntext:\" "
        + summarized_text + " \"\n\nsentiment:",
        temperature=0,
        max_tokens=20,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    s_score = sentiment_score['choices'][0]['text'].strip().upper()

    return s_score


def summarizer_text(result, tokens):
    """
        summarizer algorithm
    """

    # defining the number of chars
    if len(result) > 16000:
        chars_number = 4000
    else:
        chars_number = int(len(result)/4)

    # dividing the transcript in segment of chars' number
    s_score_lst = []
    num_iters = int(len(result)/chars_number)
    summarized_text = ""
    for i in range(0, num_iters + 1):
        print(chars_number)
        start = i * chars_number
        end = (i + 1) * chars_number
        out = summarizer_api(result[start:end], tokens)
        out = out['choices'][0]['text'].strip(":")
        sentiment = sentiment_analyzer(out)
        if sentiment == 'POSITIVE':
            s_score_lst.append('POSITIVE')
        elif sentiment == 'NEUTRAL':
            s_score_lst.append('NEUTRAL')
        elif sentiment == 'NEGATIVE':
            s_score_lst.append('NEGATIVE')
        summarized_text += out

    return summarized_text, s_score_lst


def create_word_cloud(result):
    """
        create a wordcloud chart with the original transcript
    """

    # saving a text file
    file = open('audio_text/summary.txt', 'w')
    file.write(result)
    file.close()
    stop_words = get_stop_words('english')
    name_cloud_img = 'img_gif/cloud.jpg'
    cloud = stylecloud.gen_stylecloud(file_path='audio_text/summary.txt',
                                      icon_name='fas fa-cloud',
                                      output_name=name_cloud_img,
                                      collocations=False,
                                      custom_stopwords=stop_words)

    return name_cloud_img


def text_to_asl(summarized_text):
    """
        text to american language sign
    """

    # specify the img directory path
    path = "signs_00/"

    # list files in img directory
    files = os.listdir(path)

    symbols = 'abcdefghijklmnopqrstuvwxyz_-!\',;? '
    alphabet_to_img = {s: '' for s in symbols}

    for file in files:
        # make sure file is an image
        if file.endswith(('.jpg', '.png')):
            alphabet_to_img[file.lower()[0]] = Image.open(
                os.path.join(path, file))

    white_img_symbols = '%.+=():1234567890"/<>'
    for l in white_img_symbols:
        alphabet_to_img[str(l)] = Image.open(os.path.join(path, ' .jpg'))

    alphabet_to_img["’"] = Image.open(os.path.join(path, "'.jpg"))
    alphabet_to_img["\n"] = Image.open(os.path.join(path, ' .jpg'))

    # charachters to images
    gif_lst = [alphabet_to_img[i.lower()] for i in summarized_text]

    # filepaths
    fp_out = "img_gif/image.gif"

    # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
    img = gif_lst[0]  # extract first image from iterator
    img.save(fp=fp_out, format='GIF', append_images=gif_lst,
             save_all=True, duration=400, loop=0)

    return fp_out
