# Average distance made by plane per person in Switzerland in 2015
This code computes the average distance made by plane per person in Switzerland (Swiss residents) in 2015, in km, based on the data of the Transport and Mobility Microcensus (<a href="www.are.admin.ch/mtmc">MTMC</a>). 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for reproducing the result and understanding how it has been generated. 

### Prerequisites

To run the code itself, you need python 3, pandas and numpy.

For it to produce the results, you also need the raw data of the Transport and Mobility Microcensus 2015, not included on GitHub. These data are individual data and therefore not open. You can however get them by asking the Swiss Federal Statistical Office (FSO), after signing a data protection contract. Please ask mobilita2015@bfs.admin.ch, phone number 058 463 64 68. The cost of the data is available in the document "<a href="https://www.are.admin.ch/are/de/home/medien-und-publikationen/publikationen/grundlagen/mikrozensus-mobilitat-und-verkehr-2015-mogliche-zusatzauswertung.html">Mikrozensus Mobilität und Verkehr 2015: Mögliche Zusatzauswertungen</a>"/"<a href="https://www.are.admin.ch/are/fr/home/media-et-publications/publications/bases/mikrozensus-mobilitat-und-verkehr-2015-mogliche-zusatzauswertung.html">Microrecensement mobilité et transports 2015: Analyses supplémentaires possibles</a>".

### Run the code

Please copy the files <em>zielpersonen.csv</em> and <em>reisenmueb.csv</em> that you receive from FSO in the folder "data". Then run <em>run_distance_by_plane_in_switzerland_in_2015.py</em>. 

DO NOT commit or share in any way these two CSV-files! These are personal data.

## Contact

Please don't hesitate to contact me if you have questions or comments about this code: antonin.danalet@are.admin.ch

## Acknowledgment

Thanks to Jean-Luc Muralti, who has helped by answering to multiple questions about this result.
