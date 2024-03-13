let SpeechRuleJS = {
    name: "英語/中文",
    id: "smith.bilangual_ce1",
    author: "TTS Server",
    version: 2,
    tags: {English: "英語", Chinese: "中文"},
    
    handleText(text) {
        const list = [];
        let tmpStr = "";
        let defaultTag = /[\u4e00-\u9fa5]/.test(text)?"Chinese":"English";
        
        text.split("").forEach((endchar, index) => {
            tmpStr += endchar;
            // There should be a mark in the end of the text.
            //  ⒠ for english, ⒞ for chinese
            //  ⒨ for male, ⒡ for female, ⒝ for boy, and ⒢ for girl
            switch (endchar) {
                case '⒨':
                    // Todo: implement character tags
                case '⒡':
                    // Todo: implement character tags
                case '⒝':
                    // Todo: implement character tags
                case '⒢':
                    // Todo: implement character tags
                    
                    if (defaultTag === "English") {
                        list.push({text: tmpStr, tag: defaultTag});
                    }else{//"Chinese"
                        list.push({text: tmpStr, tag: defaultTag});
                    }
                    break;
              
              default:
                    if (index === text.length - 1){
                        list.push({text: tmpStr, tag: defaultTag});
                    }
                    break;
            }
        });

        return list;
    },

    splitText(text) {
        let separatorStr = "。？?！!;；\n"

        let list = []
        let tmpStr = ""
        text.split("").forEach((char, index) => {
            tmpStr += char

            if (separatorStr.includes(char)) {
                list.push(tmpStr)
                tmpStr = ""
            } else if (index === text.length - 1) {
                list.push(tmpStr);
            }
        })

        return list.filter(item =>  item.replace(/[“”]/g, '').trim().length > 0);
    }

};