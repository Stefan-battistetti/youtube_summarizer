# import std libraries
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from gtts import gTTS
from funcs import *
import base64
import time

# Write a title
st.title('Youtube-Video summarizer')
st.subheader('Get the summary of a youtube video')

st.markdown('##')
st.write(
    'Decide the size of summary')
my_range = ['Short', 'Medium', 'Long']
dict_range = {'Short': 20, 'Medium': 60, 'Long': 100}
token_ratio = st.select_slider('Summary size', options=my_range)
youtube_link = st.text_input(
    'Please, give me the link of the video, you would like to summarize the text from')

st.markdown('###')
if youtube_link:
    # gif from local file
    time.sleep(2)
    st.markdown('###')
    st.write('While Waiting...')
    time.sleep(3)
    file_ = open('img_gif/giphy.gif', "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=True,
    )
    st.markdown('###')
    st.text('')
    st.markdown('###')
    # calling functions for transcript and summarization
    transcript = youtube_transcript(youtube_link)
    summarized_text, s_score_lst = summarizer_text(
        transcript, tokens=dict_range[token_ratio])

    st.title('EDA of the video\'s transcript')

    st.markdown('###')
    # # line chart count of species per island
    st.subheader(
        'Sentiment chart')
    st.markdown('#')
    st.write(
        'Lineplot based on the sentiment analysis during time from the original video')

    # Plotting seaborn
    fig, ax = plt.subplots()
    ax = sns.lineplot(y=s_score_lst, x=[*range(len(s_score_lst))])
    ax.set_xlabel("Video Segment", fontsize=20)
    ax.set_ylabel("Sentiment", fontsize=20)
    st.pyplot(fig)

    # create wordcloud
    st.markdown('###')
    st.subheader(
        'Wordcloud')
    st.markdown('#')
    st.write('Wordcloud chart of the original video\'s transcript')
    st.image(create_word_cloud(transcript))

    # changing tokens make the summary shorter, essential
    st.markdown('###')
    st.header('Summary of the video')
    st.write(summarized_text)

    # gif from local file
    st.markdown('###')
    st.header("Summary in ASL")
    st.write('As a experiment we propose the summary in american sign language')
    gif_name = text_to_asl(summarized_text)
    file_ = open(gif_name, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
        unsafe_allow_html=True,
    )

    # text to speech transcription from the video
    st.markdown('###')
    st.text('')
    st.header('Audio of the video\'s summary')
    st.write(
        'In case for you listening is better than reading, here you have the summary read')
    tts = gTTS(summarized_text)
    tts.save('audio_text/output_00.mp3')
    audio_file = open('audio_text/output_00.mp3', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/ogg', start_time=0)
