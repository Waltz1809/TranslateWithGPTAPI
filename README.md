# TranslateWithGPTAPI
Just a smol translate with gpt api for Waltz translate some Chinese Novel
For trans.py

    pip install openAI
    pip install yaml

Requirement for translate file is .yaml with struct:

    id: Chapter_1_Segment_1
    title: abcxyz
    content: |-
    blablabla
   
   Can use with split_content.py to split content from .txt to .yaml with many segment
   For split_content.py: 

       pip install cn2an
Requirement for content file is .txt with struct:

    number title
	    content abcxyz
Example: 
   

     第一章夫妻 | 第1章夫妻 | 1夫妻 
       　　「老婆，我晚點回家。」
        　　「路滿，你又喝酒！」
   
   

> In this case, the program detect  chapter and number by the word "第" and "章"

   Can detect Arabian Number or Chinese Number. 
   And spaghetti code. So maybe don't mind it.
By the way, you also need to write some prompt file for GPT too. 
System and Prompt file. Default is system.txt and assistant.txt
