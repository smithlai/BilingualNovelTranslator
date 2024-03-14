# BilingualNovelTranslator

我想閱讀外語小說，並藉由翻譯註解來輔助閱讀。  
但考量到時間以及保護視力，我最初打算做一款雙語有聲書。  
後來發現在閱讀軟體以及TTS方面都已經有人做出非常好的應用了，像是  
[靜讀天下(Moon+ Reader)](https://play.google.com/store/apps/details?id=com.flyersoft.moonreader)  
[tts-server-android](https://github.com/jing332/tts-server-android)。  
那麼，我需要做的就只是提供雙語小說文件。  
這可以很輕易的使用LLM API來達成。  
  
但即便如此，也有一些看似簡單，但細節充滿陷阱的prompt。  
這個專案就是用來示範如何一步一步try&error的紀錄。  
  
--------

I want to read foreign language novels and use translated annotations to assist my reading.  
However, considering time and eye protection, I initially intended to create a bilingual audiobook app.   
Later, I discovered that there are already excellent applications for reading software and text-to-speech (TTS), such as  
[靜讀天下(Moon+ Reader)](https://play.google.com/store/apps/details?id=com.flyersoft.moonreader)  
[tts-server-android](https://github.com/jing332/tts-server-android).  
So, all I need to do is provide bilingual novel files. This can be easily achieved using the LLM API.  
  
However, even so, there are some seemingly simple prompts that are full of traps in the details.  
This project is designed to demonstrate how to record step-by-step try-and-error processes.  
  

## Prerequisite

You have to install jupyterlab first.  
Here's the guide:  
https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html  
  
I personally recommand using docker.  
https://jupyter-docker-stacks.readthedocs.io/en/latest/  

## Start
### Jupyter lab
1. Fill in the .env file
2. Start docker
    ```shell
    docker run --rm -p 8888:8888  -v ./:/BilingualNovelTranslator jupyter/minimal-notebook bash -c "\
    pip install -qU python-dotenv langchain tqdm \
    langchain-google-genai langchain-openai jupyterlab_widgets ipywidgets && \
    jupyter lab --ip 0.0.0.0 --ContentsManager.allow_hidden=True \
    --allow-root --notebook-dir='/BilingualNovelTranslator' --NotebookApp.token=''"
    ```
    **Note**: Always remember to pip install the following libraries
    ```shell
        pip install -qU python-dotenv langchain tqdm langchain-google-genai langchain-openai jupyterlab_widgets ipywidgets
    ```

3. Open 127.0.0.1:8888 in your browser

###  console
```shell
pip install -qU python-dotenv langchain tqdm langchain-google-genai langchain-openai

python bilingual_translator.py alice_in_wonderland.txt

```
