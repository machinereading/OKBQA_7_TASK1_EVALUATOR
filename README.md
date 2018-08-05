[OKBQA_7_TASK1_EVALUATOR](http://7.okbqa.org/hackathon/task/task1)
===============
OKBQA Platform
-----------------

# Introduction
As research in the field of artificial intelligence has been activated, studies have been attracting more attention to building humanized knowledge as a structured knowledge base for understanding machines and utilizing such a knowledge base. These knowledge bases are used for improved information retrieval systems such as the Google Knowledge Graph or as a foundation for the services of AI agents like Apple Siri, Amazon Echo, and IBM Watson.

OKBQA (Open Knowledge Base and Question Answering) is a community aimed at constructing such a knowledge base and a question and answer system using a knowledge base, especially supporting the architecture and platform for resource disclosure and integration and collaboration. OKBQA has been working with Hackathon in 2014 and international exchanges such as Colling and SIGIR to exchange technology with domestic and international experts and build systems.

In OKBQA Hackathon in 2018, **Task 1. OKBQA Platform aims** :

+ to learn how to use OKBQA frameworks and modules
+ to learn how to contribute to OKBQA system and evaluate it

# Goals
OKBQA platform is knowledge-based QA system composed of various sub modules. The knowledge base is constructed from RDF (Resource Description Framework) data composed of <Entity 1, Attribute, Entity 2>. In order to access this knowledge base, a query such as SPARQL must be used.

To provide intuitive ways of accessing this data, a process is required to interpret and convert the user's natural language queries (e.g., "How many students in KAIST?") into SPARQL queries.

Task 1. OKBQA Platform provides opportunities to utilize and improve pre-built frameworks, architectures, and sub-modules. More specifically, we aim to:

+ Encourage participation of OKBQA collaboration platform through hands-on training
+ Understanding the question answering system technologies and dataset
+ Establishing your own question answering system through small contribution to OKBQA system
+ Integration and evaluation in OKBQA architecture

# Evaluation
Evaluator is a module to evaluate given question answering system, based on the user's choice of modules. Users can make use of configuration options to choose which modules to use for the steps of QA system, and data options to choose which QA-dataset to use for the evaluation. Once evaluator runs, it sends a natural language question in answer dataset to Controller one-by-one. It compares true answer of the dataset with the answer list from Controller. More details on QA-dataset, Input and Output can be found in below.

## QA-dataset
The dataset follows the format below.

||Description|Type|Required|
|:----|:----|:----|:----|
|id|Question's id|string or number|O|
|lang|Language of natural language question|string|O|
|question|Natural language question|string|O|
|answer|The gold answer you can get with the gold sparql|list|O|
|type|type of the answer|string|X|
|sparql|The gold sparql to get the gold answer|string|X|

We have a default QA-dataset(only English). The default QA-dataset is a modification of [QALD-3 data](https://drive.google.com/file/d/0BysRW2MnP3JSM0xEbDdaX1owT00/view) for our dataset format and can be downloaded at here: [ws.okbqa.org/down/](http://ws.okbqa.org/down/)
+ dbpedia_train_answers.json : 93 QAs excluding 7 QAs with invalid answer in QALD-3.
+ sample.json : 6 sample data from 'dbpedia_train_answers.json'. It is set as the default QA-dataset.

Here is a sample from 'dbpedia_train_answers.json':

```
[    

    {

        "id": "62",

        "lang": "en",

        "question": "Who created Wikipedia?",

        "answer": [

            "http://dbpedia.org/resource/Jimmy_Wales",

            "http://dbpedia.org/resource/Larry_Sanger"

        ],

        "type": "resource",

        "sparql": "PREFIX dbo: <http://dbpedia.org/ontology/>\nPREFIX res: <http://dbpedia.org/resource/>\nSELECT DISTINCT ?uri\nWHERE {\n\tres:Wikipedia dbo:author ?uri .\n}"

    }

]
```

## Input


