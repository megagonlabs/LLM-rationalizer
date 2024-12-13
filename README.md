# LLM-rationalizer
Repository corresponding to the ACL 2024 paper titled "[Characterizing Large Language Models as Rationalizers of Knowledge-intensive Tasks](https://aclanthology.org/2024.findings-acl.484/)." The goal of this work was to study the case of Large Language Models (LLMs) leveraging external knowledge to explain the rationales behind another model's decision-making process, specifically for knowledge-intensive tasks (KITs). In particular, we explored how humans as end-users of such rationales accept and interpret such rationales and how mistakes by LLMs or KIT models impact their trust and confidence.
![rationale generation](/images/rationale-design.png)

# Rationale Generation

In this repository, we are only releasing the rationale generation prompt template in the `prompts` [directory](/images/prompts/). 

Note that the knowledge graph extraction pipeline utilizes the [QAGNN](https://github.com/michiyasunaga/qagnn/tree/main/utils) repository. We exclude the pipeline code due to copyright constraints of the source repository.

# Study Interface Design

We conducted three studies. Two of those studies involved crowd workers on Amazon Mechanical Turk and the other involved expert users. 

## Crowdsourcing study 

To conduct the crowd study, we designed an HTML-based UI for navigating through the HITs and completing a number of rating questions. The UIs were launched at Amazon Mechanical Turk [requester service](https://requester.mturk.com/create/projects/new). The crowd study interfaces are in the `/studies/crowdsourcing/` directory.

### Comparison Study Interface

![comparison study](/images/interfaces/compare-task-feedback.png)


### Acceptability Study Interface

![acceptability study](/images//interfaces/acceptable-task-feedback.png)


## Expertsourcing study 
To conduct the expert study, we designed a Flask-based app with Jinja-powered UI and SQLite as the database for collecting and persisting data. The UI was launched at remote AWS Elastic Beanstalk service. The end-to-end study system, along with the study questions, are in the `/studies/expertsourcing/` directory. To launch the system, run the following command:

```bash
cd studies/expertsourcing/
python application.py
```

### Accountability study interface
Following is an example of a task.
![accountability task](/images/interfaces/accountability-task.png)

All the participants responed the following survey after completing the study.
![accountability survey](/images/interfaces/accountability-survey-questions.png)

# Citation and Contact
For more details on the study framework and insights read our technical paper at [ACL 2024](https://aclanthology.org/2024.findings-acl.484/). Cite our work as follows: 
```
@inproceedings{mishra-etal-2024-characterizing,
    title = "Characterizing Large Language Models as Rationalizers of Knowledge-intensive Tasks",
    author = "Mishra, Aditi  and
      Rahman, Sajjadur  and
      Mitra, Kushan  and
      Kim, Hannah  and
      Hruschka, Estevam",
    editor = "Ku, Lun-Wei  and
      Martins, Andre  and
      Srikumar, Vivek",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2024",
    month = aug,
    year = "2024",
    address = "Bangkok, Thailand",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-acl.484",
    doi = "10.18653/v1/2024.findings-acl.484",
    pages = "8117--8139"
}
```

# Disclosure

Embedded in, or bundled with, this product are open source software (OSS) components, datasets and other third party components identified below. The license terms respectively governing the datasets and third-party components continue to govern those portions, and you agree to those license terms, which, when applicable, specifically limit any distribution. You may receive a copy of, distribute and/or modify any open source code for the OSS component under the terms of their respective licenses. In the event of conflicts between Megagon Labs, Inc. Recruit Co., Ltd., license conditions and the Open Source Software license conditions, the Open Source Software conditions shall prevail with respect to the Open Source Software portions of the software. 
You agree not to, and are not permitted to, distribute actual datasets used with the OSS components listed below. You agree and are limited to distribute only links to datasets from known sources by listing them in the datasets overview table below. You are permitted to distribute derived datasets of data sets from known sources by including links to original dataset source in the datasets overview table below. You agree that any right to modify datasets originating from parties other than Megagon Labs, Inc. are governed by the respective third party’s license conditions. 
All OSS components and datasets are distributed WITHOUT ANY WARRANTY, without even implied warranty such as for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE, and without any liability to or claim against any Megagon Labs, Inc. entity other than as explicitly documented in this README document. You agree to cease using any part of the provided materials if you do not agree with the terms or the lack of any warranty herein.
While Megagon Labs, Inc., makes commercially reasonable efforts to ensure that citations in this document are complete and accurate, errors may occur. If you see any error or omission, please help us improve this document by sending information to contact_oss@megagon.ai.

All datasets used within the product are listed below (including their copyright holders and the license conditions).
For Datasets having different portions released under different licenses, please refer to the included source link specified for each of the respective datasets for identifications of dataset files released under the identified licenses.

| ID | Dataset | Modified | Copyright Holder | Source Link | License | 
|------|-----------|------------|------------|-------------|-------|
| 1 | CSQA | Yes | Tel-Aviv University | [source](https://www.tau-nlp.org/commonsenseqa) | [MIT License](https://github.com/jonathanherzig/commonsenseqa/issues/5) |
| 2 | ECQA | Yes |  IIT Delhi, IBM Research | [source](https://github.com/dair-iitd/ECQA-Dataset) | [Community Data License Agreement - Sharing - Version 1.0](https://github.com/dair-iitd/ECQA-Dataset/blob/main/LICENSE.md#community-data-license-agreement---sharing---version-10)  |
