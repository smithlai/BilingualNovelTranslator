import argparse
import utils
import sys, os

def easy_version_paragraph(llm, paragraphs, target_file, start=0):
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers.string import StrOutputParser
    prompt = PromptTemplate.from_template(
"""You are a professional novel writer. Your task is to rewrite certain passages of a novel into a much easier version for non-English adult readers.

Do not skip the chapter title if you found one

The passages came from ORC with a lots or type.
You should fix the typos and other mistakes, but you can just skip a sentence full of nonsense garbled characters.

In your output, every sentence or dialog should be separated and distinct.
Please make sure there is a line break after every complete sentence.

Just output the rewritten content, do not output any thing else.

----
The original passages is as following:

{input}

""")
    print(f"using llm: {llm}")
    chain = prompt | llm | StrOutputParser()
    revision=[]
    if 'ipykernel' in sys.modules: # Jupyter lab
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm

    if start<=0:
        start=0
        try:
            os.remove(target_file)
        except OSError:
            pass

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
                    return errorindx,revision;
 
                revision.append(temp)
                with open(target_file, 'a+') as f:
                    f.write(temp)
                    # f.write('\n')
            progress_bar.update(1)
    return errorindx,revision;


def save_to_book(json_markdowns, target_file):
    import re
    import json

    pattern = re.compile(r"```json(.*?)```", re.DOTALL)
    matches = pattern.findall("\n".join(json_markdowns))

    merged_list = []

    for match in matches:
        try:
            from json_repair import repair_json
            json_data = repair_json(match.strip(), return_objects=True)
            merged_list.extend(json_data)
        except json.JSONDecodeError as e:
            print(e)
            print(f"Error decoding JSON in block: {match}")

    with open(target_file, "w+") as f:
        for ele in merged_list:
            f.write("" + ele["zh-tw"] + "\n")
            f.write("" + ele["correction"] + "\n\n")

def handle_execution(fn, paragraphs, llm, target_file, backupllm=[], startindex=0):
    progress=0
    errorindx=startindex
    all_translated_paragraphs=[]
    while (progress < len(paragraphs)):
        errorindx, _translated_paragraphs = fn(llm, paragraphs, target_file, start=errorindx)        
        if errorindx < 0:
            progress=len(paragraphs)
            all_translated_paragraphs.extend(_translated_paragraphs)
        else: # errorindx >= 0:# error, retry
            _errorindx = -1 #temp
            for _llm in backupllm: # use optional llm to retry
                _paragraphs = paragraphs[errorindx:errorindx+1]
                _errorindx, _translated_paragraphs = fn(_llm, _paragraphs, target_file, start=0)
                if _errorindx < 0: # retry success
                    break
            if _errorindx < 0: # any retry success
                all_translated_paragraphs.append(_translated_paragraphs)
                errorindx=errorindx+1 # continue next
                progress = errorindx
                continue
    return errorindx, all_translated_paragraphs

def do(args):
    geminipro, openai = utils.init_llm()
    utils.monkeypatch_split_text_with_regex()
    split_paragraph = utils.split_paragraph

    basename = os.path.basename(args.source)
    
    paragraphs = split_paragraph(args.source)
    if args.simple:
        print("*"*8 +" Simplifying... " + "*"*8)
        simple_file = basename + ".simple"
        errorindx, paragraphs = handle_execution(easy_version_paragraph, paragraphs, geminipro, simple_file, backupllm=[openai])

    print("*"*8 +" Translating... " + "*"*8)
    translated_file = basename + ".json.txt"
    autoprocess_paragraph = utils.autoprocess_paragraph
    errorindx, translated_markdowns = handle_execution(autoprocess_paragraph, paragraphs, geminipro, translated_file, backupllm=[openai])

    print("*"*8 +" Output Formating... " + "*"*8)
    book_file = basename + ".zh-tw.txt"
    save_to_book(translated_markdowns, book_file)


def main():
    
    parser = argparse.ArgumentParser(description='Bilingual Novel Parser')



    parser.add_argument('source', help='source txt file')
    parser.add_argument('-s', '--simple', action='store_true', help='rewrite to simple version')
    parser.add_argument('--chunk_size', default=1024, help='Slice the source into file with chunk_size')
    # parser.add_argument('--max_token', action='store_true', help='rewrite to simple version')
    args = parser.parse_args()

    do(args)

if __name__ == "__main__":
    main()