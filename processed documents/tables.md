
|||
| - | - |
| Question: What is the angle of the Tower of Pisa? ||
| Passage Retrieval | Prior to restoration work performed be- tween 1990 and 2001, the tower leaned at an angle of 5.5 degrees, but the tower now |
|| leans at about 3.99 degrees. This means the top of the Leaning Tower of Pisa is dis- placed horizontally 3.9 meters (12 ft 10 in) from the center. |
| Sentence Retrieval | Prior to restoration work performed be- tween 1990 and 2001, the tower leaned at an angle of 5.5 degrees, but the tower now |
|| leans at about 3.99 degrees. |
| Proposition Retrieval | The Leaning Tower of Pisa now leans at |
|| about 3.99 degrees. |




| | # units | Avg. # words |
| - | - | - |
| Passage | 41,393,528 | 58.5 |
| Sentence | 114,219,127 | 21.0 |
| Proposition | 256,885,003 | 11.2 |

Table 1: Statistics of text units in the English Wikipedia dump from 2021-10-13.




| Retriever | Granularity | NO || T?A || WebQ || SQUAD || EQ || Avg. ||
|||| R@5 R@20  || R@5 R@20  || R@5 R@20  || R@5 R@20  || R@5 R@20  || R@5 R@20  |
| - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Unsupervised Dense Retrievers ||||||||||||||
| SimCSE | Passage | 28.8 | 44.3 | 44.9 | 59.4 | 39.8 | 56.0 | 29.5 | 45.5 | 28.4 | 40.3 | 34.3 | 49.1 |
|| Sentence | 35.5 | 53.1 | 50.5 | 64.3 | 45.3 | 64.1 | 37.1 | 52.3 | 36.3 | 50.1 | 40.9 | 56.8 |
|| Proposition | 41.1 | 58.9 | 52.4 | 66.5 | 50.0 | 66.8 | 38.7 | 53.9 | 49.5 | 62.2 | 46.3 | 61.7 |
| Contriever | Passage | 42.5 | 63.8 | 58.1 | 73.7 | 37.1 | 60.6 | 40.8 | 59.8 | 36.3 | 56.3 | 43.0 | 62.8 |
|| Sentence | 46.4 | 66.8 | 60.6 | 75.7 | 41.7 | 63.1 | 45.1 | 63.5 | 42.7 | 61.3 | 47.3 | 66.1 |
|| Proposition | 50.1 | 70.0 | 65.1 | 77.9 | 45.9 | 66.8 | 50.7 | 67.7 | 51.7 | 70.1 | 52.7 | 70.5 |
| | Supervised Dense Retrievers |||||||||||||
| DPR | Passage | 66.0 | 78.0 | 71.6 | 80.2 | 62.9 | 74.9 | 38.3 | 53.9 | 47.5 | 60.4 | 57.3 | 69.5 |
|| Sentence | 66.0 | 78.0 | 71.8 | 80.5 | 64.1 | 74.4 | 40.3 | 55.9 | 53.7 | 66.0 | 59.2 | 71.0 |
|| Proposition | 65.4 | 77.7 | 70.7 | 79.6 | 62.8 | 75.1 | 41.4 | 57.2 | 59.4 | 71.3 | 59.9 | 72.2 |
| ANCE | Passage | 70.7 | 81.4 | 73.9 | 81.4 | 65.7 | 77.2 | 43.3 | 58.6 | 57.0 | 69.1 | 62.1 | 73.5 |
|| Sentence | 70.3 | 81.6 | 73.9 | 81.5 | 65.2 | 77.4 | 45.8 | 60.7 | 61.4 | 72.8 | 63.3 | 74.8 |
|| Proposition | 69.9 | 81.1 | 72.8 | 80.6 | 65.1 | 77.1 | 46.2 | 61.9 | 66.7 | 76.6 | 64.1 | 75.5 |
| TAS-B | Passage | 64.2 | 77.9 | 70.4 | 79.3 | 65.1 | 77.0 | 54.3 | 69.2 | 72.2 | 81.3 | 65.2 | 76.9 |
|| Sentence | 64.0 | 78.4 | 71.4 | 80.2 | 63.9 | 76.7 | 58.9 | 72.3 | 72.7 | 82.0 | 66.2 | 77.9 |
|| Proposition | 63.8 | 78.6 | 71.4 | 80.0 | 63.8 | 76.8 | 59.8 | 73.4 | 75.1 | 83.3 | 66.8 | 78.4 |
| GTR | Passage | 66.3 | 78.4 | 70.1 | 79.4 | 63.3 | 76.5 | 54.4 | 68.1 | 71.7 | 80.5 | 65.2 | 76.6 |
|| Sentence | 66.4 | 79.4 | 71.6 | 80.9 | 62.2 | 76.8 | 60.9 | 73.4 | 72.5 | 81.3 | 66.7 | 78.4 |
|| Proposition | 66.5 | 79.6 | 72.2 | 80.9 | 63.2 | 77.4 | 63.3 | 75.0 | 74.9 | 83.0 | 68.0 | 79.2 |

Table 2: Passage retrieval performance (Recall@k = 5, 20) on five different open-domain QA datasets when pre-trained dense retrievers work with the three different granularity from the retrieval corpus. Underline denotes cases where the training split of the target dataset was included in the training data of the dense retriever.



 Retriever | Granularity | NQ || TQA || WebQ || SQUAD || EQ || Avg. ||
||| EM || EM || EM || EM || EM || EM ||
|||| @100 @500  | @100 | @500 | @100 | @500 | @100 | @500 | @100 | @500 || @100 @500  |
| - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| | Unsupervised Dense Retrievers |||||||||||||
| SimCSE | Passage | 8.1 | 16.3 | 22.6 | 33.7 | 7.7 | 14.9 | 9.8 | 17.8 | 10.9 | 17.5 | 11.8 | 20.0 |
|| Sentence | 10.1 | 18.0 | 27.2 | 37.2 | 9.6 | 15.6 | 17.3 | 24.8 | 13.0 | 19.8 | 15.4 | 23.1 |
|| Proposition | 12.7 | 20.2 | 28.4 | 37.7 | 11.2 | 17.2 | 18.0 | 25.1 | 18.3 | 25.0 | 17.7 | 25.0 |
| Contriever | Passage | 11.1 | 22.4 | 25.7 | 41.4 | 6.8 | 14.9 | 15.6 | 27.7 | 10.9 | 21.5 | 14.0 | 25.6 |
|| Sentence | 13.8 | 23.9 | 30.5 | 44.2 | 9.1 | 17.2 | 22.6 | 32.8 | 12.2 | 22.2 | 17.6 | 28.1 |
|| Proposition | 16.5 | 26.1 | 37.7 | 48.7 | 13.3 | 19.9 | 25.6 | 34.4 | 16.1 | 27.3 | 21.8 | 31.3 |
| | Supervised Dense Retrievers |||||||||||||
| DPR | Passage | 24.8 | 36.1 | 40.3 | 51.0 | 14.0 | 22.2 | 12.4 | 21.7 | 18.6 | 25.9 | 22.0 | 31.4 |
|| Sentence | 27.6 | 35.9 | 44.6 | 52.8 | 16.3 | 23.7 | 18.6 | 26.1 | 21.8 | 28.2 | 25.8 | 33.3 |
|| Proposition | 28.3 | 34.3 | 45.7 | 51.9 | 19.0 | 23.8 | 19.8 | 26.3 | 26.3 | 31.9 | 27.8 | 33.6 |
| ANCE | Passage | 27.1 | 38.3 | 43.1 | 53.1 | 15.2 | 23.0 | 15.3 | 26.0 | 23.4 | 31.1 | 24.8 | 34.3 |
|| Sentence | 30.1 | 37.3 | 47.0 | 54.7 | 16.6 | 23.8 | 22.9 | 30.5 | 25.9 | 32.0 | 28.5 | 35.7 |
|| Proposition | 29.8 | 37.0 | 47.4 | 53.5 | 19.3 | 24.1 | 22.9 | 30.1 | 29.1 | 33.7 | 29.7 | 35.7 |
| TAS-B | Passage | 21.1 | 33.9 | 39.3 | 50.5 | 13.1 | 20.7 | 23.9 | 34.6 | 30.9 | 37.3 | 25.7 | 35.4 |
|| Sentence | 24.6 | 33.9 | 43.6 | 52.3 | 14.4 | 21.4 | 33.8 | 40.5 | 31.4 | 36.1 | 29.6 | 36.8 |
|| Proposition | 26.6 | 34.0 | 44.9 | 51.8 | 18.1 | 23.7 | 34.2 | 38.9 | 34.2 | 37.8 | 31.6 | 37.2 |
| GTR | Passage | 23.4 | 34.5 | 38.7 | 49.3 | 13.1 | 20.1 | 23.9 | 33.8 | 31.3 | 36.7 | 26.1 | 34.9 |
|| Sentence | 26.8 | 35.1 | 43.9 | 52.2 | 15.9 | 21.6 | 35.6 | 41.3 | 31.3 | 35.1 | 30.7 | 37.1 |
|| Proposition | 29.5 | 34.4 | 45.9 | 52.6 | 18.7 | 23.8 | 37.0 | 40.4 | 34.1 | 37.1 | 33.0 | 37.7 |

Table 3: Open-domain QA performance (EM = Exact Match) under retrieve-then-read setting where the number of retrieved words to the reader QA model is limited at l = 100 or 500. We use UnifedQA V2 (Khashabi et al., 2022) as the reader model. The first l words from the concatenated top retrieved text unit are feed as input to the reader model. Underline denotes cases where the training split of the target dataset was included in the training data of the dense retriever. In most cases, we see better QA performance with smaller retrieval units.



ecent works on dense retrievers typically adopt a dual-encoder architecture (Yih et al., 2011; Reimers and Gurevych, 2019; Karpukhin et al., 2020; Ni et al., 2022). With dual-encoders,
:unselected: :unselected: :unselected:
| Passage Retrieval | Sentence Retrieval | Proposition Retrieval |
| - | - | - |
| Q1: What was the theme of Super Bowl 50? | | |
| Title: Super Bowl X ? The overall theme of the Super Bowl enter- tainment was to celebrate the United States Bicentennial. Each Cowboys and Steelers player wore a special patch with the Bicen- tennial logo on their jerseys ... :selected: :selected: | Title: Super Bowl X ? The overall theme of the Super Bowl entertainment was to celebrate the United States Bicentennial. :selected: :selected: | Title: Super Bowl XLV ? ... As this was the 50th Super Bowl game, the league [Super Bowl 50] emphasized the "golden anniversary" with various gold- themed initiatives during the 2015 season, as well as ... :selected: |
| Q2: The atomic number of indium which belongs to 5th period is? |||
| Title: Period 5 element ? The periodic table is laid out in rows to illus- trate recurring (periodic) trends in the chemi- cal behaviour of the elements as their atomic number increases: ... :selected: | Title: Period 5 element ? Indium is a chemical element with the symbol In and atomic number 49. :selected: | Title: Period 5 element ? Indium is a chemical element with the sym- bol In and [Indium has a] atomic number 49. This rare, very soft, malleable ... :selected: |
| Q3: What is the function of the pericardial sac? |||
| Title: Pericardium ? The pericardium, also called pericardial sac ... It separates the heart from interference of other structures, protects it against infection :selected: | Title: Pericardium ? The pericardium, also called pericar- dial sac, is a double-walled sac con- taining the heart and the roots of the great vessels. :selected: | Title: Cardiac muscle ? On the outer aspect of the myocardium is the epicardium which forms part of the pericar- dial sac that surrounds, protects, and lubri- :selected: |
| and blunt trauma, and lubricates the heart's || cates the heart. |
| movements. || |
| Q4: What is the main character's name in layer cake? |||
| Title: Layer Cake (film) ? ... The film's plot revolves around a London- based criminal, played by Daniel Craig, ... Craig's character is unnamed in the film and is listed in the credits as "XXXX". :selected: | Title: Angelic Layer ? The primary protagonist is Misaki Suzuhara. :selected: | Title: Plot twist ? Sometimes the audience may discover that the true identity of a character is , in fact, unknown [in Layer Cake] , as in Layer Cake or the eponymous assassins in V for Vendetta and The Day of the Jackal. :selected: |

Table 4: Example cases where top-1 retrieved text unit of each retrieval granularity fails to provide the correct answer. The underlined text is the correct answer. The gray text is the context of propositions, but it is for illustration purpose only and not provided to the retrievers and downstream QA models.