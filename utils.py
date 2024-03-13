
def init_llm():
    # Remember to fill you api key in .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
    
    safety_settings = {
        # Gemini blocks everything
        # HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE, 
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, 
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    geminipro = ChatGoogleGenerativeAI(model="gemini-pro",
                                    temperature=0.5, top_p=0.85, 
                                     safety_settings=safety_settings,
                                    convert_system_message_to_human=True) #SystemMessages are not yet supported!
    
    
    from langchain_openai import OpenAI, ChatOpenAI
    
    openai = OpenAI(max_tokens=2048)
    return geminipro, openai


from typing import List
def _split_text_with_regex(
    text: str, separator: str, keep_separator: bool
) -> List[str]:
    import re
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = [_splits[i] + _splits[i + 1] for i in range(0, len(_splits)-1, 2)]
            if len(_splits) % 2 == 1:
                splits += _splits[-1:]
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]



# Monkey patch
def monkeypatch_split_text_with_regex():
    from langchain_text_splitters import character
    character._split_text_with_regex = _split_text_with_regex

def split_paragraph(source_path):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=0,
        separators= ["[\"\.!\?”][\s\t]?\n\n\n\n",
                     "[\"\.!\?”][\s\t]?\n\n\n",
                     "[\"\.!\?”][\s\t]?\n\n",
                     "[\"\.!\?”][\s\t]?\n"
                    ],
        # length_function=len,
        keep_separator=True,
        is_separator_regex=True,
    )
    content=""
    with open(source_path, 'r') as f:
        content = f.read()
    
        
    return text_splitter.split_text(content)

def _repair_markdown_json(bad_markdown_json):
    from json_repair import repair_json
    import json, re
    pattern = re.compile(r"```json(.*?)```", re.DOTALL)
    matches = pattern.findall(bad_markdown_json)
    merged_list = []
    for match in matches:
        try:
            json_data = repair_json(match.strip(), return_objects=True)
            new_json = json.dumps(json_data, indent=4, ensure_ascii=False)
            # print(new_json)
            merged_list.append(new_json)
        except json.JSONDecodeError as e:
            print(e)
            print(f"Error decoding JSON in block: {match}")
    return "\n".join(["```json"] + merged_list +["```\n"])

def autoprocess_paragraph(llm, paragraphs, target_file, start=0):
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers.string import StrOutputParser
    prompt = PromptTemplate.from_template(
"""You are a professional translation assistant. Your task is to translate a paragraph from english to traditional Chinese.

There will be an OCR document with many layout issues.
You should first try to find out every complete sentence and speech in the article,
and check and fix it if the sentence or speech got split(linebreak) by mistake.
Every sentence or speech should be separated and distinct.
Your shoud check and fix misspellings and typos a well.

Then you should translate each sentence into zh-tw.
If a sentence is nonsense, you can just copy it to the correction and translation fields without any modification.

The output should be a markdown code snippet formatted in the following json schema, including the leading and trailing "```json" and "```":

```json
[
    {{
        "correction": string  // the sentence after error correction
        "zh-tw": string  // the translated sentence zh-tw
    }},
    {{
        "correction": string  // the sentence after error correction
        "zh-tw": string  // the translated sentence zh-tw
    }},
    .......
    ........
    {{
        "correction": string  // the sentence after error correction
        "zh-tw": string  // the translated sentence zh-tw
    }}
]
```

Example:
---
input:

Eefore one girl and another even younger one stood a figure in 
full p1ate armor brandishing a 5word.Lhe blade swung, sparkl-
ing in the sun1ight as if to say that taking their lives in a 
single stroke would be an act of mercy.
"No, let me go" She begged.
""
---
output:

```json
[
    {{
        "correction": "Before one girl and another even younger one stood a figure in full plate armor brandishing a sword.",
        "zh-tw": "在一名少女以及比她更年輕的少女面前，站著一位身穿全身板甲、揮舞著劍的男子。"
    }},
    {{
        "correction": "The blade swung, sparkling in the sunlight as if to say that taking their lives in a single stroke would be an act of mercy."
        "zh-tw": "刀鋒揮動，在陽光下閃爍，彷彿在說一刀奪命是仁慈的作為。"
    }},
    {{
        "correction": "“No, let me go”"
        "zh-tw": "不，放我走。"
    }},
    {{
        "correction": "She begged."
        "zh-tw": "她如此哀求著。"
    }},
]
```
---


The original paragraph is as following:

{input}

""")
    print(f"using llm: {llm}")
    chain = prompt | llm | StrOutputParser()
    translated=[]
    from tqdm.notebook import tqdm, trange
    errorindx = -1
    with tqdm(total=len(paragraphs)) as progress_bar:
        for i, paragraph in enumerate(paragraphs):
            if i < start:
                progress_bar.update(1)
                continue
            if len(paragraph.strip()) > 0:
                try:
                    # temp = ""
                    # for chunk in chain.stream({"input": paragraph}):
                    #     print(chunk, end="", flush=True)
                    #     temp += chunk
                    # print("\n------\n")    
                    temp = chain.invoke({"input": paragraph})
                except Exception as e:
                    print(f"Error occurs at {i}:")
                    print(paragraph)
                    print(e)
                    errorindx = i
                    return errorindx,translated;
                    
                temp = _repair_markdown_json(temp)
                # retry=0
                # temp2 = temp
                # while retry < 3:  # We retry to fix this 3 times, if we cannot fix it, just don'y touch it.
                #     err_msg = verify_json(temp2)
                #     if err_msg:
                #         temp2 = fix_json(llm, temp2, err_msg)
                #         retry += 1
                #         if retry == 3:
                #             print("Invalid Json:\n")
                #             print(f"{temp}\n")
                #             print(f"{err_msg}\n")
                #         continue
                #     temp = temp2
                #     break;
                        
                translated.append(temp)
                with open(target_file, 'a+') as f:
                    f.write(temp)
                    f.write('\n')
            progress_bar.update(1)
    return errorindx,translated;

