## Monitoring Strategies for Assessing Hypoxia Risk Inflight......................................................... 68

## Severe Acute Hypoxia Concerns................................................................................................ 69

## Transition to Exploration Atmosphere...................................................................................... 70

## Hyperoxia .................................................................................................................................. 71

# SECTION IV: Directed Acyclic Graphs............................................................................................ 72

## Decompression Sickness Directed Acyclic Graph...................................................................... 72

### DCS Integration with Other Risks: ......................................................................................... 74

## Hypoxia Directed Acyclic Graph ................................................................................................ 74

### Hypoxia Integration with Other Risks:................................................................................... 75

# SECTION V: Knowledge Base......................................................................................................... 76

## Decompression Sickness Knowledge Base................................................................................ 76

## Hypoxia Knowledge Base .......................................................................................................... 76

# SECTION VI: Conclusions ............................................................................................................... 78

# REFERENCES.................................................................................................................................. 80
---
# Acronyms

|       |                                                            |
| ----- | ---------------------------------------------------------- |
| 1-G   | Earth-normal gravity                                       |
| AFB   | Air Force Base                                             |
| AGE   | arterial gas emboli                                        |
| AMS   | acute mountain sickness                                    |
| ATA   | atmosphere pressure absolute                               |
| ATM   | atmosphere pressure                                        |
| BGI   | bubble growth index                                        |
| BMI   | body mass index                                            |
| BTA   | bends treatment adapter                                    |
| CEVIS | cycle ergometer with vibration isolation and stabilization |
| CNS   | central nervous system                                     |
| CO₂   | carbon dioxide                                             |
| DCS   | decompression sickness                                     |
| ΔP    | pressure difference                                        |
| EMU   | Extravehicular Mobility Unit                               |
| EVA   | extravehicular activity                                    |
| FFW   | feet fresh water                                           |
| FSW   | feet sea water                                             |
| ft    | foot                                                       |
| HLS   | Human Landing System                                       |
| hr    | hour                                                       |
| ID    | identification                                             |
| ISLE  | in-suit light exercise                                     |
| ISS   | International Space Station                                |
| JSC   | Johnson Space Center                                       |
| kg    | kilogram                                                   |
| k     | number of gas species in tissue                            |

---
|                 |                                               |
| --------------- | --------------------------------------------- |
| kPa             | kilopascal                                    |
| LEA             | launch, entry and abort                       |
| μG              | microgravity                                  |
| m               | meter                                         |
| min             | minute                                        |
| ml              | milliliter                                    |
| mmHg            | millimeters of mercury (pressure)             |
| n               | sample size                                   |
| NASA            | National Aeronautics and Space Administration |
| NBL             | Neutral Buoyancy Laboratory                   |
| NEEMO           | NASA Extreme Environment Mission Operations   |
| N₂              | nitrogen                                      |
| O₂              | oxygen                                        |
| P₁              | initial pressure                              |
| P1N₂            | computed tissue N₂ partial pressure           |
| P2              | final pressure                                |
| PB              | prebreathe                                    |
| P(DCS)          | probability of decompression sickness         |
| P(Grade IV VGE) | probability of Grade IV VGE                   |
| PI              | Principal Investigator                        |
| P(Serious DCS)  | probability of serious decompression sickness |
| PFO             | patent foramen ovale                          |
| P₁N₂            | inspired (wet) partial pressure of nitrogen   |
| P₁O₂            | inspired (wet) partial pressure of oxygen     |
| pN₂             | partial pressure of nitrogen                  |
| pO₂             | partial pressure of oxygen                    |
| PRP             | Prebreathe Reduction Protocol                 |
| psia            | pounds per square inch absolute               |

---
|          |                                                                   |
| -------- | ----------------------------------------------------------------- |
| R-value  | ratio-value used by NASA, equivalent to P1N2 / P2, also called TR |
| SCUBA    | self-contained underwater breathing apparatus                     |
| SD       | standard deviation                                                |
| STPD     | standard temperature (0 Celsius), pressure (1 ATM), dry gas       |
| STS      | Space Transportation System                                       |
| TR       | tissue ratio                                                      |
| U.S.     | United States                                                     |
| USAF     | United States Air Force                                           |
| VGE      | venous gas emboli                                                 |
| VO₂ peak | measured peak oxygen consumption as ml·kg⁻¹·min⁻¹                 |
| WWII     | World War II                                                      |

---
# Executive Summary

Extravehicular activity (EVA, also known as 'spacewalks') is at the core of NASA's human space exploration program. Although initial phases of space exploration rely heavily on remotely operated robots, sustained and extensive exploration tasks – as well as some critical tasks and contingencies – are best performed by human crewmembers working in conjunction with robotic systems.

To allow for rapid and effective human physical presence, NASA needs a safe and efficient EVA program as part of any human exploration program. This entails minimal EVA preparation time, rapid access to the field sites of interest, and short turnaround/recovery times while minimizing maintenance. Due to the minimal to non-existing atmospheres of current near-term destinations (Moon and cis-lunar space, Mars, and nearby asteroids), minimizing suit pressure and maximizing operational flexibility is a necessity.

The last decade of EVA operations has been limited to the International Space Station (ISS). Microgravity EVAs on the ISS are infrequent (only a handful per year) and focus on maintenance and upgrades of a human-centric engineered structure. Exploration EVAs, however, represent a paradigm shift, aiming to perform frequent EVAs up to 24hrs of EVA per crew per week which is comparable to the current *annual* EVA time on the ISS. Furthermore, many will be on natural structures and planetary surfaces, something that has not occurred since the Lunar EVAs in the Apollo Program.

Before the first EVA, NASA understood that decompression sickness (DCS) was a risk that needed to be mitigated. Given the highly constrained spaceflight environment, these mitigation strategies must be efficient regarding both time and resources. In addition, a clear understanding of the underlying causative mechanisms of DCS is needed to efficiently mitigate this potentially catastrophic risk to the mission and the crewmember. Should DCS occur in the spaceflight environment, it would likely occur during an EVA, when the crewmember is already isolated from the habitat in a physically constraining spacesuit. Historically, treatment for DCS can only begin once the crewmember has terminated EVA activities and returned to the habitat to be repressurized, but with new technologies (i.e., variable pressure space suits), initial treatment can be started during an EVA. However, definitive treatment will still require additional pressure from the habitat.

In order to adapt to frequent surface EVA operations, NASA has been preparing for almost two decades. One of the key changes has been to set aside the ISS/Shuttle sea-level atmosphere – critical for scientific research, where comparison to Earth environments is key – and return to a low pressure, oxygen-enriched atmosphere that minimizes inert gas loads.

Commissioned in 2005, the Exploration Atmospheres Working Group (EAWG) had the primary goal of recommending internal atmospheres to NASA to enable efficient and repetitive EVAs for missions that were to be enabled by the former Constellation Program. At the conclusion of the
---
EAWG meeting, the 8.0 psia and 32% oxygen (O₂) environment was recommended for EVA-intensive phases of exploration missions.

After re-evaluation in 2012, the 8.0 psia / 32% O₂ environment was altered to 8.2 psia and 34% O₂ to reduce the hypoxic stress to a crewmember by increasing alveolar O₂ pressure by 11 mmHg, which is expected to significantly benefit crewmembers. The 8.2 psia / 34% O₂ environment (inspired O₂ pressure = 128 mmHg) is also physiologically similar to the staged decompression atmosphere of 10.2 psia / 26.5% O₂ (inspired O₂ pressure = 127 mmHg) used on 40 different Shuttle missions for approximately one week during each flight. A review of historical atmospheres used by NASA is presented in Figure 1.

As a result of selecting this exploration atmosphere, NASA gains the capability for efficient EVA operations with low risk of DCS, but not without incurring the additional negative stimulus of hypobaric hypoxia to the already physiologically challenging spaceflight environment. This report provides a review of the Human Health and Performance decompression risks primarily associated with EVA and their mitigation. The focus will be on decompression sickness, hypoxia, and the use of the 8.2 psia / 34% O₂ environment during spaceflight and oxygen prebreathe (PB) prior to EVA to denitrogenate the body prior to depressurization events. Other areas of focus include validation of the DCS mitigation strategy, incidence, and management of transient acute mountain sickness (AMS) and prevention of oxygen toxicity during hyperoxic exposures (such as during O₂ PB and DCS treatment). To be able to implement and support operations at novel atmospheres, the physiologic research and operational validation of exploration-focused atmospheres and space suits is critical.
---
# Atmospheric Composition

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A graph showing pressure (psia) on the y-axis (0-14) versus percent O2 on the x-axis (0-100). The graph contains several labeled regions and data points: - International Space Station (at \~14 psia, \~21% O2) - 6000ft point (at \~12 psia, \~21% O2) - Shuttle Staged/ISS Campout (at \~10.2 psia, \~26.5% O2) - 14000ft point (at \~8 psia, \~21% O2) - Exploration Atmosphere (at \~8.2 psia, \~34% O2) - Skylab (at \~5 psia, \~70% O2) - Mercury/Gemini/Apollo (at \~5 psia, \~100% O2) - EMU (at \~4.3 psia, \~100% O2) The graph shows regions labeled: - Hypoxia (left side, low O2 percentage) - Normoxia (middle region) - Hyperoxia (right side, high O2 percentage) Lines indicate: - Hypoxia Limit (piO2 2.4 psia) - Normoxia (piO2 3 psia) - Hyperoxia Limit (piO2 6 psia, long term exposure) Red arrows indicate: - "Increased DCS Risk" (pointing down-left) - "Increased Fire Risk" (pointing right) Vertical lines mark: - \~21% O2 (Earth atmosphere) - 30% Flammability Limit (Shuttle/ISS) - 34% Flammability Limit (Proposed) - 70% O2 Materials Limit |

*Figure 1: Historical atmospheric compositions and the proposed Exploration Atmosphere by pressure/oxygen composition*

While hypoxia and DCS are related, both involve the removal of an environmental parameter: O2 for hypoxia and ambient pressure for DCS, they are still very different environmental physiology risks. In addition, there is no physiologically advantageous reason for the crew to be exposed to any amount of hypoxia, therefore the only driving reason for potential nominal hypoxic exposures is due to the reduced pressure atmospheres required to mitigate DCS to acceptable risk with less operational impacts. Thus, while these risks are intertwined, the causes, mitigation approaches, research strategies, vehicle design impacts, and operational controls during phases of the mission are all different. Therefore, this Evidence Report will primarily address each risk in separate sections, but also show how these risks are connected.
---
# SECTION I: Decompression Sickness

**Risk Statement:** *Given that decompression sickness (DCS) is a potential risk for every spaceflight/mission (e.g., EVA or cabin depressurization) and must be mitigated to acceptable risk levels; limitations in quantitative understanding of DCS will lead to conservative DCS risk mitigation countermeasures with significant operational, engineering, and/or secondary health/performance impacts.*

## Introduction: Fundamentals of Decompression Sickness

> "An ounce of prevention is worth a pound of cure."
> - Benjamin Franklin

Understanding the fundamental physical and physiological processes that happen following pressure changes remains elusive. Similar to deep saturation divers and high-altitude mountaineers, human space exploration challenges our understanding of human physiology, biochemistry, and physics beyond our current knowledge. Although observed for centuries, the impacts of the pressure and oxygen changes on the body cannot be clearly nor easily predicted, and treatments to recover from such exposure are based on experience as much as a fundamental understanding of the processes at hand. Thus, we must aim to prevent events that are not clearly predictable.

The first scientific study of hypoxia and DCS began in the 17th century, as technological developments allowed scientists to explore the effects of changing atmospheric conditions in laboratory environments. Robert Hooke, an assistant researcher to Robert Boyle, created the first functional vacuum pump in 1671 [1]. The development of air pumps and compressors in the 17th and 18th centuries opened the field of hyperbarics, including the ability to supply air to deeper depths. Paul Bert's seminal treaties on barometric pressure codified in 1878 much of the empirical experience of the day [2]. Diving technology rapidly advanced, permitting deeper and longer exposures to hyperbaric air with the accompanying DCS on the return to 1 atmosphere absolute (ATA). Several books detailing the history of diving chronicle the methods to prevent DCS on return to the surface and on treatment strategies to aid those afflicted with "the bends." A compilation of experience with hypobaric (altitude) DCS was published by Fulton in 1951, succinctly titled, *Decompression Sickness*. No other book has since been published to surpass the depth and breadth of information that lies between the covers of Fulton's book. Much of what we know about hypobaric DCS and denitrogenation as a mitigation was learned during and shortly after World War II (WWII) and was summarized in in Fulton [3]. Numerous chapters and reports have since been published that include new observations and evidence for hypobaric DCS, summarized in the following sections.
---
Humans are typically subjected to Earth-normal atmospheric pressure at sea level (1 ATA, 14.7 psia, 101.3 kPa, 760 mmHg) and Earth-normal gravity (1-G). This Earth-normal atmosphere is just one pressure in a range of higher and lower pressures where humans can comfortably exist. Rapid decreases in pressure are the primary driver for DCS. As a result, NASA Requirements JPR 1830.61, "Requirements Applicable to Personnel Participating in Diving, Hyper/Hypobaric Chambers, and Pressurized Suit Operations" has been developed to provide DCS mitigation strategies for environments with known DCS risk. Spaceflight DCS mitigation strategies are documented in flight procedures and flight rules and will be summarized in this document.

## Decompression Sickness Signs and Symptoms

DCS signs and symptoms are historically classified as Type I, Type II, and skin bends. At NASA Johnson Space Center (JSC), Type I DCS symptoms are described as "pain only", localized in muscle(s) or joint(s). While pain is the most common Type I symptom, others can include a single localized paresthesia and simple skin bends. Type I symptoms can result in an EVA termination/abort and jeopardize mission success. If not treated, Type I symptoms can eventually become incapacitating and jeopardize EVA crew member recovery.

Type II symptoms are systemic, involving the central nervous system, cardiopulmonary system (resulting in pulmonary "chokes"), circulatory collapse, shock, and even death, and may include multiple site paresthesia. Type II symptoms require immediate termination of an EVA and jeopardize both mission success and crew health. Type II symptoms may or may not be preceded by Type I symptoms and may be life threatening, especially in the EVA environment if not abated by an increase in pressure and adjunctive treatment.

Cutis Marmorata is a type of skin bends more serious than Type I skin bends where the skin has a marbled or mottled appearance. It likely indicates that significant bubble formation is occurring throughout the body. At NASA JSC, this type of skin bends is categorized separately from Type I and Type II DCS.

DCS is also associated with gas embolism (the presence of gas bubbles in the vascular system), both venous gas emboli (VGE) and arterial gas emboli (AGE). Although VGE can typically be adequately filtered by the lung, circulating VGE is not a desired condition, especially with the presence of a patent foramen ovale (PFO), which is a hole in the wall separating the right and left atria of the heart. A PFO is a remnant of fetal circulation, where oxygenated blood from the placental circulation is shunted away from the pulmonary circulation of the fetus. This connection closes in most newborns, but about 25% of the adult population has some small patency (hole) that allows oxygenated and deoxygenated blood to mix. If denitrogenation efforts are not effective, either due to inadequate vehicle design (either in gas constituency and/or atmospheric pressure) or inadequate operational PB protocols, then the resulting presence of VGE during an EVA could, under certain conditions, cross through a PFO and become arterialized. Many factors

1 https://cdms.nasa.gov/assets/docs/centers/JSC/Dirs/JPR/JPR1830.6.pdf
---
in the aerospace environment compromise healthy lung function. These factors, when combined with a high number of VGE entering the pulmonary circulation, can put astronauts at high risk of arterializing VGE that are normally filtered by a healthy lung. AGE put crewmembers at risk of vascular blockages and resulting ischemic damage to brain or other organs.

The displacement of tissue by trapped gas spaces or the disruption of metabolic function due to embolic obstruction of blood flow can cause a wide range of signs and symptoms. The historical approach to DCS mitigation at NASA has been very conservative, with the goal of preventing DCS. One consistent observation concerning test subjects at NASA JSC is that pain only DCS after significant decompression stress is predominately found in the lower body, particularly associated in or around the patella [4, 5].

## Causes of Decompression Sickness

There are two conditions necessary for the development of DCS. The first is inert gas supersaturation, defined as a tissue inert gas partial pressure greater than ambient pressure. The second is the presence of a bubble nuclei (micronuclei) from which the supersaturated tissue inert gas can evolve into a gas bubble.

### Supersaturation

A fundamental axiom about DCS is that a transient gas supersaturation, also called over-pressure or pressure difference (ΔP), exists in a tissue region; the sum of all gas partial pressures in that region is greater than the ambient pressure opposing the release of the gas. Expressed as an equation, supersaturation exists when ΔP is positive:

$$\Delta P = \sum_{i=1}^{n} (P_i - P_2)$$ (Eq. 1)

where P₁ is the dissolved gas tension of the i^th gas of n species in the tissue, and P₂ is the ambient pressure after depressurization. The potential for bubble nucleation and rate of bubble growth are a function of the supersaturation.

Gas supersaturation in the tissue is not in itself harmful but is a thermodynamically unstable condition between the tissue and the surrounding environment. The difference between tissue gas partial pressure and ambient pressure is easily resolved with a phase transition, and some of the excess mass (moles) of gas in the form of bubbles may be accommodated by the tissue and cause no symptoms. However, whenever a gas space is formed due to partial or complete desaturation of a supersaturated tissue there is some probability of DCS [P(DCS)] [6]. A necessary condition for DCS is the formation of a gas phase in the tissue. The assumption that pain results from the deformation of tissue past a critical point due to evolved gas may not account for symptoms other than pain only DCS, but evolved gas is certainly the primary insult for all subsequent signs and symptoms. It is not the presence or even the volume of evolved gas in the
---
tissue that is important in pain only DCS, but the pressure difference between the gas space and the tissue. The pressure difference is termed "deformation pressure" [7].

## *Bubble Nuclei (Micronuclei)*

Minimizing the pressure differential, and/or the use of oxygen PB to reduce the amount of tissue N₂ that can support bubble growth. But another approach to DCS prevention is to also to hinder the transformation of tissue micronuclei into growing bubbles [8, 9]. The presence of gaseous micronuclei in the tissues can result in DCS under modest depressurizations [10]. Information about and evidence for tissue micronuclei come mostly from indirect observations. The application of a high-pressure spike, either hydraulic or pneumatic, filtration, or ultracentrifugation of a sample are all accepted means to reduce the number and size of micronuclei (change the distribution), evident from fewer bubbles or cases of DCS after a subsequent depressurization [11-13]. One inference from these studies is that normal physical activity establishes a size distribution of micronuclei within tissues, which can be modified by changing activity level. The idea of "clearing" micronuclei faster than they are generated as a means to understand increased resistance to DCS on repeated exposures has also been discussed [14]. A comprehensive review and discussion of micronuclei is not provided here, but information is available in numerous sources [14-21]

## *Diving (Ascent from Depth)*

Long before humans could ascend to high altitude, including space, they could dive to modest depths using compressed air or be exposed to modest depths using caissons in tunnel and bridge-building projects. Diving on compressed air or exposure to compressed air in a caisson allows for additional nitrogen (N₂) to accumulate in tissues, based on the solubility of N₂ in the tissues and the delivery of N₂ by the circulatory system. Ascent (effectively, depressurization) limits for these exposures were empirically derived based on avoiding supersaturation of mathematically derived tissue half-time compartments pioneered by John Haldane, and decompression models using that approach are referred to as "Haldanian". The depth and duration of the dive (hyperbaric exposure) defines the controlling half-time compartments to limit the supersaturation specific to the compartment. At a certain point, divers can remain long enough at increased pressure to the point where no additional N₂ is absorbed by the tissues at the exposure depth; these are called saturation exposures. Ascent from saturation exposures is slower than for non-saturation exposures since the total dissolved N₂ is greater and the high N₂ partial pressure has come into equilibrium in tissues with long half-times, which require longer time to denitrogenate during ascent back to 1 ATA.

DCS is a known risk in the diving community and is mitigated through diver training and widespread use of decompression tables or dive computers, which use a decompression model to determine dive time limits, ascent rates, and decompression stops during ascent. For a more detailed discussion on diving-related DCS and dive physiology, the reader is referred to Bennett and Elliott's Physiology and Medicine of Diving [22].
---
## Diving Astronaut

In human spaceflight, the main focus of DCS prevention surrounds EVAs, but it should be noted that training for EVAs includes the culmination of many hours of training under both hyperbaric and hypobaric conditions. For example, in training for ISS assembly EVAs, it was normal for a crewmember to train in the JSC Neutral Buoyancy Laboratory (NBL) at a ratio normally exceeding 10 NBL hours per 1 EVA hour [23]. Policies and procedures are followed that minimize the P(DCS) after hyperbaric suited exposures in the NBL and the Russian Hydrolab, during suited exposures in hypobaric chambers, and after diving activities from Aquarius, the NASA Extreme Environment Mission Operations (NEEMO) underwater habitat. Training in the NBL emulates actual EVA scenarios in an actual spacesuit (pressurized to match the same pressure difference expected in light) and can last for ~6 hours. Crewmembers are pressurized to approximately 21psia maximum physiological pressure, equivalent to a depth of 40 feet of fresh water (FFW) (pool depth) and 4psia suit pressure. To avoid DCS from these exposures, astronauts breathe a nitrox mixture of 46% O₂ and 54% N₂. With the nitrox breathing gas, the equivalent air depth is ~23 FFW. Thus, breathing nitrox eliminates the need for decompression stops at the end of long training sessions in the NBL. Additional details about the NBL's diving practices are available in Fitzpatrick and Conkin [24].

Astronauts also train and maintain proficiency in operating the spacesuit under hypobaric conditions in various altitude chambers at JSC. In some cases, astronauts are required to fly in the T-38 aircraft or on commercial airlines shortly after a hyperbaric or hypobaric exposure. Specific directives, based on best available research [25-27], dictate proper surface intervals and PB procedures to minimize the P(DCS) on a subsequent hypobaric exposure.

Procedures and equipment are available to treat DCS on-orbit and after training activities, and a disposition policy (NASA JSC JPR 1800.3E²) returns astronauts to flight status after a successful treatment regime. Adherence to these policies and procedures, which undergo periodic review and updates, minimize the chance that DCS will become a medical concern to the astronaut or hinder the completion of training or safe execution of an EVA.

## Ascent to Altitude / Depressurization to EVA Suit Pressure

A diver experiencing DCS will do so upon return to the surface after completing their dive (i.e., going from a higher pressure at depth to a lower pressure at the surface); treatment in such circumstances ideally starts immediately and requires little action on the part of the patient. In contrast, an aviator that loses cabin pressure or astronaut during an EVA in a spacesuit would be afflicted with DCS during the performance of their tasks rather than at the completion. The aviator/astronaut must typically return themselves or be returned to a safe environment and configuration by a co-pilot or EVA buddy before treatment for evolved gas can be initiated. Thus, in addition to the health risk associated with any occurrence of DCS, an occurrence of DCS during

² https://cdms.nasa.gov/assets/docs/centers/JSC/Dirs/JPR/JPR1800.3.pdf

15
---
spaceflight carries the additional risk associated with delayed initiation of treatment as well as the secondary concern of the potential for loss of mission objectives.

The most effective way to reduce P(DCS) is to reduce the ΔP between environments, either by reducing P₁ (cabin inert gas [primarily N₂] partial pressure) or increasing P₂ (suit pressure), or some combination of both to achieve acceptable risk and operational efficiency. A spacesuit is essentially a flexible, portable spacecraft; details about U.S. spacesuits are available from Thomas and McMann [28]. The current NASA spacesuit, called the Extravehicular Mobility Unit (EMU), operates at 4.3 psia (222 mmHg) in the vacuum of space [29, 30]. Current EMU suit technology, especially in the design of gloves, does not allow for a high-pressure suit without increased fatigue, reduced mobility, and decreased manual dexterity. However, the Russian space program accepts some of these human performance decrements and operates their Orlan suit at 5.8 psia. Historically, reducing the risk of DCS by increasing suit pressure has implied significant operational limitations, but future suits aim to be adjustable to various pressures, operating effectively between 3.7 and 8.2 psia.

If the pressure difference between the habitat and the suit cannot be sufficiently narrowed, breathing oxygen (oxygen PB) prior to exposure to the low-pressure environment of the spacesuit allows the body to off-gas nitrogen without incurring any supersaturation, or DCS risk. However, PB requires use of crew time just prior to an actual EVA, decreasing available EVA time, and adds complexity of managing 100% oxygen systems at high pressure environments.

## Human Spaceflight Evidence – Decompression Sickness

No reported cases of DCS have occurred in astronauts or cosmonauts working in spacesuits pressurized to between 3.7 and 5.8 psia during EVAs. In contrast, U.S. and Russian research subjects who evaluate operational PB protocols in altitude chambers report about 20% DCS [31]. Technicians have reported pain only DCS at JSC during suit development (two cases are documented in an internal NASA Investigation Report from 1988), and at least 1 astronaut recalled experiencing pain (considerably after the spaceflight) in one knee on 2 occasions after depressurization to 5.0 psia in the spacecraft [32]. Foster and Butler [33] discussed several factors that may reduce the P(DCS) in EVA astronauts working in hypobaric and microgravity environments, which are summarized in this section.

### DCS Symptom Reporting

A research setting designed specifically to monitor for DCS is fundamentally different from an operational setting where a highly trained and motivated crewmember is performing an EVA, which is considered one of the pinnacles of an astronaut's career. Even if DCS symptoms have occurred, there may be a bias to not report mild discomfort in this type of an operational setting, especially if symptoms are not limiting. NASA's current policy is that every test subject and every
---
crewmember who participate in hyperbaric or hypobaric operations are required to immediately report the onset of any DCS symptoms (NASA JSC JPR 1800.3E).

Under-reporting of DCS symptoms is routinely observed in pilot training where qualification to fly is compromised if DCS is reported during hypobaric training activities. This is discussed in the context of the high-altitude U-2 pilot community [34, 35], which highlight differences between operational and research reports of DCS. In Bendrick, et al. [34], 75% of a cohort of active duty and retired U-2 pilots (n=273) responding to an anonymous questionnaire said that they had experienced DCS symptoms at least once during their careers flying U-2 aircraft, but rarely reported their symptoms to the flight surgeon [36]. Further, Webb, et al. [37] reported a DCS incidence rate of 77% in subjects testing the 60-min U-2 PB protocol, which included mild exercise while at a simulated aircraft cabin pressure of 4.37 psia. Intense, short-duration exercise during this PB reduced the incidence to 42% in subjects and is offered to U-2 pilots who feel the need for additional DCS protection [38].

The only anecdotal report of a DCS symptom in an astronaut during spaceflight was reported several years after the flight in a personal autobiography rather than real-time to the flight surgeon [32]. For various reasons, astronauts and pilots are not motivated to report every small discomfort during operations [39]. As a result, it is possible that the first report of DCS during an EVA will be a serious case of DCS [40].

In addition, there are valid reasons why mild symptoms of DCS might be masked during an EVA. Many astronauts take aspirin before an EVA, so mild aches and pains are managed in advance. Operating in a pressurized suit like the EMU is also known to contribute to aches and pains comparable to pain only DCS. As such, many potentially mild cases of DCS are not reported during EVA as they are attributed to pain caused by working in the EMU. Since mild DCS symptoms often clear during repressurization, astronauts would have little incentive to report a symptom that is no longer present after the conclusion of an EVA. In validation testing in altitude chambers, the incidence of DCS symptoms that would interfere with performance in an EMU is less than 5% [41, 42]. About 85% of those with symptoms showed improvement or no change in symptom intensity when tests were allowed to proceed past the point of the first symptom report. Because PB protocols before EVA reduce the incidence and intensity of symptoms, it is understandable that any resulting mild symptoms are unremarkable in an operational setting.

## *Operational and Gravitational Benefits of the Spaceflight Environment*

It is also possible that DCS has not actually occurred during EVA [43, 44]. Limited motion, especially of the lower body, in spacesuits such as the EMU and Orlan is hypothesized to be a significant factor to actually reduce the likelihood of DCS during microgravity EVA.

Beyond limited mobility in spacesuits, the weight support and joint forces experienced by research subjects during ambulatory movements in 1-G are not present during microgravity EVA. Based on detailed analysis of actual PB performed on-orbit, Tissue Ratio (TR), computed for the
---
first 142 staged PB protocols from the Shuttle, was 1.51 ± 0.07 SD with no DCS compared to 1.52 ± 0.26 in 245 research subjects at JSC with a DCS incidence rate of 18%. Unlike astronauts in microgravity, the test subjects were ambulatory during testing [45]. Ambulation exacerbates DCS and VGE from the lower body, so the absence of ambulation in μG likely reduces the incidence of DCS below 18% during EVA [45]. During the Shuttle staged protocol, TR also decreases during subsequent EVAs, from 1.51 to 1.48 for the second EVA. This is because breathing 100% O₂ during a 6 hr EVA continues the denitrogenation over multiple EVAs during a Shuttle mission. In addition, the crew lives at 10.2 psia / 26.5% O₂, where tissues eventually equilibrate to a pN₂ of about 7.5 psia. Waligora and Pepper [46] and Waligora and Kumar [47] summarized physiological aspects of working in space during the first 59 Shuttle person-EVAs.

Astronauts also historically perform more conservative denitrogenation/PB in space than is tested on the ground, since ground-based PBs are translated into Aeromedical Flight Rules, and more than the minimum protection has always been provided in space due to the complexity of transitioning a simple research protocol into actual EVA operations. A recent example of this is from the use of the In-Suit Light Exercise (ISLE) PB protocol. DCS incidence during a ground-based study, which included a non-ambulatory EVA simulation, was 4.2%, but as the research protocol was adapted to flight operations, crewmembers undergo an additional 32 to 57 minutes of additional PB time. With this additional safety margin, the predicted risk of DCS decreases to 0.3% per EVA. As of November 2022, the ISLE protocol has been used for 130 individual EVAs with no reported DCS and remains the primary PB protocol for microgravity EVAs on the ISS.

In addition to added PB duration, we also need to understand if the primary risk mitigation strategy of prebreathing is more or less affected by adaptations to μG. All astronauts undergo significant physiological adaptation in μG [48]. About 2 liters of fluid from the lower extremities is redistributed into the chest and head, triggering diuresis with a resulting decrease in total body water. The upper body venous engorgement at the expense of a reduced lower body venous capacitance does not abate even after months in space, even with a net decrease in plasma volume. As a result of this fluid shift, denitrogenation in μG may be more efficient in space than on Earth if a supine body position is a reasonable analog for μG [49].

Additional interventions to modify N₂ washout have also been studied [50, 51]. Jones, et al. [52] performed the early work to understand the effects of blood perfusion on N₂ uptake and subsequent elimination in tissues. Several studies showed how body composition and exercise during PB influenced N₂ removal [53-55]. Other factors such as increased ambient temperature, supine body position, and immersion in water increased N₂ removal from adipose and muscle tissue, and from the entire body [49, 56-58]. Theis, et al. [59]confirmed and supplemented these data by examining whole-body N₂ washout during supine body position. Further, negative pressure breathing accelerates N₂ washout [60, 61]. Efforts to understand N₂ removal under various experimental conditions, including μG simulation, resulted in a wide range of tissue N₂ washout from about 8 ml/kg for seated subjects to about 24 ml/kg for subjects who performed 50 watts of continuous arm and leg exercise for 2 hr while in a 6-degree head-down tilt during a
---
3 hr PB [62-64]. Thus, it is reasonable to hypothesize that altered physiology and anatomy in response to μG adaptation modifies the amount of N₂ removed from the body during PB [65-67].

Following the purge of N₂ after donning the suit, an astronaut's body is surrounded by almost pure O₂ (>95%) during the suited operational PB and for the duration of the EVA. It is unclear how much N₂ is transferred out of the body through the skin, or into the body of subjects surrounded by air in altitude chambers; however, any benefit would go to the astronaut [68]. Warm, ambient temperature has been shown to enhance denitrogenation [49]. Astronauts in the Shuttle and during EVA often report they are cool to cold. It is likely that research subjects are in a more comfortable thermal environment during a PB and EVA simulation than astronauts. It is unclear how skin temperature that is cooled via the Liquid Cooling and Ventilation Garment affects the transport of N₂ across the skin during the in-suit PB and EVA. Understanding N₂ washout in space as well as the unbiased information from an in-suit Doppler bubble detector would greatly help to understand the true risk of DCS in EVA astronauts [69-71].

Astronauts are physically active during PB, as exercise during PB accelerates N₂ washout [37, 72, 73]. Aerobic fitness, as measured by VO₂ peak, is not *per se* associated with resistance to pain only DCS. While VO₂ peak in subjects exposed to hypobaric environments without PB and with resting PB failed to show a strong association with DCS, the association was strong when exercise was included as part of the PB [74, 75]. The benefit of exceptional aerobic fitness toward reducing the P(DCS) is only realized when exercise is exploited as part of the PB. A person with low VO₂ peak can reduce their P(DCS) to match a fit person by increasing the intensity of exercise in the same PB time, by increasing the length of the PB, or a combination of both [74, 76].

Cumulative O₂ consumption during PB is not the only consideration to reduce the P(DCS). Effective N₂ elimination seems to depend on how the exercise is performed more so than just total O₂ consumption per unit time normalized to body mass during PB. There are constraints as to the type and duration of exercise prescribed during PB since long, physically-demanding EVAs will occur after the PB. Female research subjects did not benefit to the same degree as men when exercise during PB was prescribed as %VO₂ peak [77]. Astronauts as a group are more physically fit than their age-matched research subject counterparts. Current astronauts are about 10 years older than research subjects, but have similar aerobic fitness as measured by VO₂ peak. Therefore, subjects who would be aged matched to the astronaut population would be less fit. If fitness is linked to DCS susceptibility [78-80], then astronauts as a group under any PB condition may be less susceptible to DCS than subjects of comparable age [81]. Finally, the "effective" exercise in the EMU might be less than or different from exercise on Earth used to simulate EVA activity, and exercise is certainly an important consideration for DCS risk at altitude.

## *Current ISS Decompression Sickness Mitigations*

Different spaceflight missions require different strategies to mitigate the risk of DCS. In every case, a detailed analysis (trade process) defines the appropriate PB. This section provides a summary of PB protocols that are currently in operational use, along with any lessons learned
---
along the way. ISS astronauts currently have three denitrogenation *strategies* available to reduce the P(DCS): 1. resting in-suit PB, 2. staged denitrogenation ("campout protocol"), and 3. exercise PB.

Desire to perform science with μG as the primary variable led NASA to select an Earth-normal atmosphere for the ISS. The Russian space program had already committed to an Earth-normal atmosphere, even before the *Mir* space station was launched. A consequence of these decisions was that EVAs in the 4.3 psia EMU and the 5.8 psia Russian *Orlan* spacesuit could result in DCS due to the large pressure difference between the habitat and suit, so efficient and effective denitrogenation PB protocols were necessary. Compounding the challenge, an air break (brief exposure to high partial pressure of N₂ (pN₂)) during a 100% O₂ PB is unavoidable if transitioning O₂ delivery from a mask to the EVA suit. This requires research to understand and procedures to compensate for air breaks in PB.

*In-suit, 4 hour Prebreathe Protocol*

In the resting PB protocol, astronauts breathe 100% O₂ in the spacesuit for 4-hr. The 4-hr duration was determined based on the need to achieve an acceptable P(DCS) considering the type and amount of work to be done in the suit and the duration of the hypobaric exposure (Conkin et al. 1987). The operational challenge is to match the length of PB with an acceptable low incidence of DCS to produce an efficient EVA system [82]. Waligora, et al. [41] describes tests of 3.5 and 4 hr PBs at JSC, which evolved into the current operational 4-hr in-suit PB. The 4-hr in-suit resting PB has been used 6 times during spaceflight with no reported DCS. However, a 4-hr prebreathe immediately prior to performing an EVA that could last up to 8 hours represents an inefficient use of crew time, makes the crew duty day over 14 hours on EVA days, and inefficiently uses up suit consumables.

*Campout Protocol*

A modification of the Shuttle staged denitrogenation protocol, called the campout protocol, significantly reduces the required in-suit PB duration by having the two EVA crewmembers "camp out" in the ISS airlock at 10.2 psia, 26.5% O₂ during the night prior to their EVA. For various operational reasons, the time at 10.2 psia is limited to 8 hr and 40 min, most of which is spent sleeping. The lack of food preparation and personal hygiene facilities in the airlock means that a post-sleep repressurization to 14.7 psia is required prior to suit donning. During this break, the 2 astronauts breathe 100% O₂ by mask for 70 min while gathering food and using the restroom. Upon return to the 10.2 psia / 26.5% O₂ environment, the masks are removed, and the suit-donning process is completed. The airlock is then repressurized to 14.7 psia after the astronauts don their spacesuits to allow the IVA crewmember who assists the EVA crew with suit donning to exit at 14.7 psia. Thereafter, the EVA crew can complete the 50 min in-suit PB before the final depressurization of the airlock to the vacuum of space with the suits remaining at 4.3 psia.
---
After extensive review, the similarity of the campout PB on ISS to the Shuttle staged PB along with operational experience with the Shuttle staged protocol negated an empirical validation of the ISS campout PB. The first EVAs from the ISS using the campout protocol took place in September 2006 with 146 person-EVAs completed since with no reports of DCS. The last use of the campout PB was in 2011 and it is no longer trained for or used. Documentation for the ISS campout PB protocol is periodically updated and could be made available for ISS crewmembers if needed.

This more complicated staged PB protocol was favored over a simpler resting, in-suit PB as the staged protocol reduces fatigue in astronauts, who would otherwise be in the spacesuit for 10 - 12 hr and increases the efficiency of the astronauts as time that would otherwise be unproductive during a 4 hour in-suit PB can be spent on other tasks. The only way to reduce fatigue and maintain efficiency while using the in-suit PB is to perform the majority of the PB while using a mask outside of the suit, but this eventually requires a transition from the mask to the suit. Since the suit requires a 100% O₂ purge and leak check, the transition from a mask, or even a mouthpiece and nose clip, to the suit with 100% O₂ without an air break has proven unavoidable.

## *Exercise Prebreathe Protocols*

After the ISS *Quest* airlock was delivered in July 2001 on STS-104.7A and before the campout protocol was available in September 2006, an option to perform exercise-enhanced denitrogenation PB protocols from the ISS became available. An accelerated denitrogenation protocol was needed to avoid scheduling constraints on EVAs performed from the ISS and since N₂ elimination and uptake is a perfusion-limited process, the use of exercise during the PB is an effective method of accelerating denitrogenation. The ambitious goal of the exercise PB protocols was to reduce the existing 4-hr resting in-suit PB by about half.

Before the delivery of the *Quest* airlock, EVAs to support ISS construction were done with hatches closed between the 2 vehicles so that the Shuttle 10.2 psia PB could be used. The first use of exercise PB was implemented for an EVA tasked to complete installation of the ISS airlock. The discomfort and complexity of adding an effective interval of exercise during PB must be balanced with the rewards: less total PB time and greater reduction in the P(DCS) compared to an alternative resting PB. No single, reasonable, short-term intervention can increase cardiac output as much as exercise. Exercise during PB was evaluated during and shortly after WW II [55, 83, 84], and reevaluated at Brooks Air Force Base (AFB) for the special operations community [37, 85-89] and most recently by NASA. Details are available for 9 exercise PB options evaluated by NASA from 1997 to 2009 [72, 76, 90, 91] and in Table 1.

The current exercise PB protocol used on the ISS is the In-suit Light Exercise (ISLE) PB protocol using the EMU as a resistive exercise device; the Exercise PB protocol using the cycle ergometer with vibration isolation and stabilization (CEVIS) device was retired in 2023.
---
In the ISLE PB protocol, 40 min are spent breathing 100% O₂ by mask followed by a 20 min depressurization to 10.2 psia. Once suit donning is complete, arm and leg motions are performed for 4 min followed by 1 min of rest in conjunction with a 5-min repressurization back to 14.7 psia. The mild exercise pattern continues for 50 min and achieves a minimum VO₂ of 6.8 ml·Kg⁻¹·min⁻¹. An additional 50 min of resting PB completes the protocol and is thereby followed by a 30 min depressurization of the airlock to vacuum. The ISLE PB is currently the prime protocol used by astronauts on the ISS and has been used 130 times as of November 2022 with no reported DCS.

The return to 14.7 psia after a short suit donning period at 10.2 psia in the ISLE PB protocol, and 2 returns to 14.7 psia over the course of the previously utilized longer campout PB protocols, likely reduces the P(DCS) through removal of silent bubbles. These bubbles have the potential to form from a limited number of large-radius micronuclei during the initial depressurization to 10.2 psia. Once formed and then subsequently reabsorbed during the repressurization to 14.7 psia while breathing 100% O₂, the tissues are temporarily left with a smaller range of micronuclei radii from which to grow bubbles during the final depressurization to 4.3 psia. Recompression did not occur during the Shuttle 10.2 psia staged depressurization protocol, but rather the entire habitable volume of the Shuttle was depressurized, so the astronauts simply continued the depressurization from 10.2 psia to 4.3 psia after suit donning in the airlock.

## *Retired Prebreathe Protocols*

The remainder of this section describes historical human spaceflight PB protocols and associated lessons learned along the way.

### *ISS - Cycle Ergometer with Vibration Isolation and Stabilization (CEVIS) Protocol*

For the CEVIS Exercise PB protocol, prior to launch the astronaut would perform a peak O₂ consumption (VO₂) test using leg ergometry, and a linear regression of VO₂ vs. watts (workload) is created for that individual. An exercise prescription is then produced that distributes the appropriate workload between the upper body (12%) and lower body (88%).

During on-orbit EVA preparations, the astronaut would breathe O₂ from a mask and perform 3 min of incremental exercise on the CEVIS at about 75 RPM using a prescription that increases work from 37.5% to 50% and then to 62.5% of their VO₂ peak while also rhythmically pulling against elastic surgical tubing to include upper body activity. The ergometry is complete after an additional 7 min at 75% of VO₂ peak. After waiting an elapsed time of 50 min while still breathing 100% O₂ from the mask, the ISS airlock is depressurized to 10.2 psia in 30 min. During the depressurization, the liquid cooling garment and the lower portion of the spacesuit are donned. Once the airlock O₂ concentration stabilizes at 26.5%, the EVA crew and IVA crew-attendant remove the masks and complete the donning of the upper torso of the spacesuit. Thus, for a significant portion of the PB duration the astronaut is physically active in the suit-donning process. A leak check is performed and then a purge with 100% O₂ to remove N₂ from the suit completes the suit-donning procedure. Thereafter, the in-suit PB starts in conjunction with a 5-min repressurization back to 14.7 psia where the remaining 55 min of in-suit PB is performed,
---
and the IVA crewmember exits the airlock. The final depressurization of the airlock to the vacuum of space and of the suit to 4.3 psia takes 30 min.

The CEVIS Exercise PB protocol was retired with the implementation of the ISLE protocol on the ISS. The CEVIS Exercise PB has been used 52 times no reported DCS and was last used 11/21/09 after a false alarm interrupted the Campout protocol causing the crew to alter plans and change PB protocols to preserve the EVA. Although successful and necessary to the construction of the ISS, the CEVIS Exercise PB protocol was the most complex of the protocols to perform, with up to 21 steps where errors or hardware failures could result in a break or inability to complete the PB, and the protocol was archived (no further training/planned use) on August 4, 2016.

### *Shuttle Staged Protocol*

In the Shuttle staged denitrogenation strategy, the ambient pressure was decreased to an intermediate pressure so that the inspired partial pressure of N2 (PIN2) was lower than the initial PIN2 [41, 92-95]. The staged depressurization approach is enhanced when O2 concentration is also increased to lessen the impact of hypoxia and to further reduce PIN2. However, the initial pressure reduction could transform a subpopulation of tissue micronuclei into "silent" bubbles, so a 60 min 100% O2 PB with a mask was performed before the initial modest reduction in ambient pressure to 10.2 psia [4, 41, 96-98].

This protocol, that ultimately became the preferred PB protocol for the Shuttle, was achieved in 3 steps:

1. Initial 60 min PB by mask, of which 45 min was completed before the Shuttle atmosphere was depressurized from 14.7 psia to 10.2 psia and the air was enriched to 26.5% O3 to provide an inspired partial pressure of O2 (PIO2) of 127 mmHg.
2. Minimum stay of 12 hr at this intermediate pressure.
3. In-suit PB before a final depressurization to 4.3 psia, lasting 40 to 75 min depending on the time spent at 10.2 psia.

Figure 2 shows the cumulative fraction of VGE detected in ground-based subjects exposed to 4.3 psia for 4 hr after 3 different PB Protocols. A related figure appears in Waligora, et al. [41]. All subjects performed EVA-simulation work activities and were ambulatory at 4.3 psia. The solid line that increases (steps) and plateaus quickly to about 45% is from 10 of 22 subjects that had VGE with a mean onset time of 43 ± 43 min standard deviation (SD). This trial did not include a 1 hr PB before a 12 hr stay at 10.2 psia / 26.5% O2. The dashed line that plateaus to about 50% VGE is from the same trial as described above except it did include a 1-hr PB before the 12 hr stay at 10.2 psia. The mean VGE onset time in 18 of 35 subjects with VGE was 105 ± 48 min. Finally, the dashed line that plateaus to about 65% VGE was from a trial with a 3.5 hr PB and a direct ascent to 4.3 psia. The mean VGE onset time in 15 of 23 subjects with VGE was 115 ± 55 min. The mean VGE onset times were statistically longer (p<0.002) when compared to the trial without the 1 hr PB before ascent to 10.2 psia for 12 hr.
---
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ```
0.750 |         |         |         |         |         |         |         |
|                                                                     |---|---|---|---|---|---|
0.625 |                                                           ----------|
|                                                      -----          |
0.500 |                                          -------------              |
|                                     -----                           |
0.375 |                    --------        -                                |
|              ------        --------                                 |
0.250 |         ----                                                        |
|     ----                                                            |
0.125 |    -         -------                                                |
| ---                                                                 |
0.000 |_|_________|_________|_________|_________|_________|_________|______|
0         30        60        90       120       150       180      210      240
time at 4.3 psia (min)
``` |

**Figure 2:** The onset time for the first detection of VGE was earlier in the trial where no PB was performed and a 12 hr exposure to 10.2 psia (solid line) before exposure to 4.3 psia compared to when a 1 hr PB was performed (dashed line with 50% peak) or when there was a direct ascent to 4.3 psia after a 3.5 hr PB (dashed line with 65% peak).

The computed decompression dose (described later) was slightly higher in the trial that omitted the initial 1 hr PB, so a higher group incidence of VGE was expected. Instead, a rapid onset of VGE was observed in a few subjects, possibly because micronuclei associated with the vascular endothelium transformed into silent bubbles ready to grow and enter the venous circulation after the final depressurization to 4.3 psia. An ascent to 10.2 psia (3,000 m, 9,750 ft) without some PB predisposed some subjects to produce VGE shortly after reaching 4.3 psia. This also occured even after spending 12 hr at 10.2 psia with a 40 min PB before the final ascent to 4.3 psia. It is notable that 5 of 10 subjects in this trial had VGE first detected within 30 min at 4.3 psia. One had VGE detected after 1 min at 4.3 psia and at 65 min had signs and symptoms classified as serious DCS. DCS was diagnosed in all 3 trials, with a 20% group incidence and a mean onset to first symptoms of about 2 hr.

Optimization of the final Shuttle 10.2 psia staged depressurization protocol took months of planning and years of validation. The first critical step was to certify the Shuttle for operations at a reduced pressure with an enriched O2 atmosphere, since the vehicle was not originally planned to operate under these conditions. Several interacting variables were evaluated in isolation or in combination including rate of ascent to intermediate pressure, the intermediate pressure itself (equipment cooling issues, [99]), the pO2 and pN2 at the intermediate pressure (hypoxia and flammability issues, [100]), length of stay ([96]), likelihood of silent bubbles, final suit pressure, duration of EVA, work performed in the suit, the final in-suit PB time before final ascent, and balancing the acceptable risk of DCS during EVA with limited treatment options [41, 101].
---
The time at spent 10.2 psia / 26.5% O₂ was not considered a break in PB since the lengthy exposure to a reduced pN₂ at 10.2 psia continued the denitrogenation process. Astronauts simply donned their suits at 10.2 psia when they were ready and performed a final 40-75 min in-suit PB before final depressurization to 4.3 psia, without the need to first repressurize to 14.7 psia. If the time spent at 10.2 psia was expected to be greater than 36 hr, then the initial 60 min mask PB at 14.7 psia was omitted. The rationale for this was that any silent bubbles formed during the 15-20 min depressurization to 10.2 psia would be reabsorbed given enough time at 10.2 psia. Although this procedure was complicated and had several operational and physiological impacts, it was preferred over the simpler but less efficient 4-hr in-suit PB. The first EVAs that used the Shuttle staged protocol were on STS-41B in February 1984, and the last of 153 person-EVAs was in 2011 with the retirement of the Shuttle.

## Skylab

Skylab provided a unique environment from which to conduct studies on adaptation to μG. The science and medical community accepted 70% O₂ at 5.0 psia since the Earth-equivalent PIO₂ would be 150 mmHg, and the risk of atelectasis was minimized since the atmosphere was 30% N₂. Scientists on Earth did not have to provide a hypoxic or hyperoxic environment as part of their ground-based control studies, so μG was the primary experimental variable. No dedicated PB was needed before EVAs from Skylab in spacesuits pressurized to 3.7 psia since the tissues would eventually equilibrate to a computed tissue N₂ partial pressure (P¹N₂) of no more than 1.2 psia, far below the suit pressure. Various restrictions, such as uncomfortable flame retardant polybenzimidazole clothing, were imposed due to the serious risk of fire in a 70% O₂ atmosphere. In the end, Skylab was a success and the need to confront several technical issues early in the mission showed that an effective EVA capability was critical to the success of long-duration missions.

## Apollo and Gemini

A minimum 3-hr in-suit PB was performed before launch in all NASA programs prior to the Shuttle [93]. This protected inactive astronauts from DCS after reaching orbit; during ascent cabin pressure was reduced from 14.7 psia to 5.0 psia and the atmosphere was simultaneously enriched to 100% O₂ [29]. Although this PB was effective in most cases, 1 astronaut wrote, years after leaving the space program, that he had symptoms consistent with DCS while at 5.0 psia. Michael Collins on Gemini X and later on Apollo 11 believed he had symptoms of pain only DCS in his left knee that eventually resolved in the 100% O₂ atmosphere as the missions proceeded [32]. This was not an unexpected outcome based on prior PB validation trial reports [93, 102]. Astronauts on subsequent EVAs from the Apollo spacecraft, Skylab, and on the Lunar surface in suits pressurized to 3.7 psia were not at risk for DCS due to denitrogenation achieved during their extended time in the hypobaric and hyperoxic breathing environment.
---
## Human Terrestrial Evidence – Decompression Sickness

Validation testing often precedes the implementation of a PB protocol in space operations. The first test of PB protocols occurred in August 1982, with DCS reported after a 3.5-hr PB in one subject and a Doppler Technician [31, 42]. This was an inauspicious start to the validation of a 3.5-hr PB. A 4-hr PB reduced the incidence of DCS from 42% to 21% and reduced the incidence of VGE from 71% to 46% in data normalized to a 6 hr exposure to 4.3 psia in men that ambulated as part of exercise while at 4.3 psia [41, 42]. On April 12, 1981, the Shuttle STS became a reality. The first EVA from the Shuttle was on April 7, 1983, using a 3.5 hr baseline in-suit PB. Only 3, two-person EVAs have been performed from the Shuttle after a 3.5 or 4 hr in-suit PB since April of 1983. The 4 hr in-suit PB remained an option throughout the Shuttle program and remains the fall-back option on ISS should something in the ISLE protocol result in an unrecoverable break in prebreathe.

The inefficiency of in-suit PB and the possibility of a break in PB during transition from the O₂ mask to the spacesuit required that NASA validate the staged 10.2 psia protocol in the early 1980's. Variations of similar protocols soon emerged, along with a desire to summarize all the results with a simple decompression dose. In addition to the DCS outcomes, routine ultrasound bubble monitoring provided an unbiased assessment of the decompression dose. The Spencer 0 – IV categorical scale [103, 104] was adopted, and the following standard 4 min evaluation scheme to improve bubble detection and grading was implemented at JSC [105]: A Doppler technician located and optimized an acceptable Doppler ultrasound blood flow signal in the pulmonary artery from a sitting or semi-recumbent subject in an altitude chamber in about 15 sec. The subject was then instructed to rhythmically flex each limb 3 times in sequence, moving all joints in the limb. The movement dislodged small bubbles sequestered in venous capillaries, and the grade of VGE passing beneath a 5.0 or 2.5 MHz ultrasound wave was assigned by an investigator outside the altitude chamber.

Figure 3 illustrates decompression dose-response curves for DCS and VGE outcomes from 341 exposures to 4.3 psia in altitude chambers at JSC. All subjects breathed 100% O₂ through a mask and were otherwise in a comfortable shirt-sleeve (i.e. non-suited) environment. The mean exposure time to 4.3 psia was 4.4 ± 1.3 hr, and subjects ambulated from one exercise station to another. Exercises included cranking and pulling against modest resistance and torquing fixture to simulate the type and intensity of work performed during a contingency EVA (further details are included in [31]. At intervals of about 15 min, the pulmonary artery was monitored with an ultrasound bubble detector in recumbent subjects. Given enough exposures over a range of decompression doses, a predictive equation for DCS and VGE was created from the Hill equation. The wide 95% confidence limits for DCS and VGE suggest that factors other than simple decompression dose influence the outcome. In addition, there is more to accepting a denitrogenation protocol than just the raw incidence of DCS or VGE: The nature of the symptoms, how the incidence of DCS is related to the intensity of the symptoms [106], and their response
---
to repressurization [107] are as important as the overall incidence of DCS and VGE to a final decision to accept a PB protocol.

![Figure 3: A graph showing P(DCS) and P(VGE) plotted against Decompression Dose as TR - 0.79. The x-axis ranges from 0.0 to 1.2, and the y-axis (labeled "P(DCS) and P(VGE)") ranges from 0.0 to 1.0. The graph shows dashed lines representing P(VGE) which are higher than solid lines representing P(DCS). Both increase as decompression dose increases. The graph includes 95% confidence limits shown as shorter lines above and below the best estimates.]

Figure 3: P(DCS) (solid lines) and P(VGE) (dashed lines) increase as decompression dose increases. The 95% confidence limits (shorter lines) above and below the best estimate help to visualize uncertainty in the outcome.

Table 1 summarizes DCS and VGE results archived at JSC in the NASA Hypobaric Decompression Sickness Database. Tests done for NASA by Brooks AFB are not shown here, but are available in the Air Force Research Laboratory Altitude Decompression Sickness Research Database archived at Wright-Patterson AFB and available through their website. Operational questions dictated the sequence of testing in Table 1. The first trials evaluated the 3.5 hr (Tests 1a and 2a) and then 4 hr in-suit PB protocols (Tests 3a and 3c), and the subjects in these protocols often "crossed over" to then validate the 10.2 psia staged PBs. Several variations of the staged protocol tested the benefit of an initial 60 min PB before depressurization to 10.2 psia, different durations at 10.2 psia, and different final in-suit PB times before depressurization to 4.3 psia (Tests 1b, 1c, 1d, 2b, 3b, 3d). Repetitive exposures to 4.3 psia while living at 10.2 psia addressed issues of fatigue and cumulative DCS and VGE risk (Tests 4a through 4f). Cumulative risk was found not to be a concern in repetitive hypobaric depressurizations [42, 108, 109], so repetitive EVAs from the Shuttle was deemed safe. Women were first included in a trial of a 6-hr PB protocol at JSC (Test 5a) and during a novel 10.2 psia staged protocol where simulated suit pressure was 6.0 psia with 60% O₂. A trial of an 8-hr resting PB (Test 5b) established the benefits of "extreme prebreathing", even if not practical from an operational perspective. The influence of high work rate during EVA was evaluated using rowing machines [93], which resulted in 2 cases classified as serious DCS from Test 7a. Exercise intended to counteract deconditioning in space did not influence the subsequent DCS and VGE outcome given that the interval between the exercise and simulated EVA was 16 hr (Tests 8a and 8b, [110]). The consequences of ambulation before and during an

27
---
altitude exposure were evaluated at both 6.5 psia and 4.3 psia in the *Argo* series, starting with Test 9a and ending with Test 11a. Test 9a included ambulatory controls and Test 9b were the same subjects but at 6-degree head-down bed rest for 3 days before and during the 3 hr exposure to 6.5 psia without prior PB. The incidence of Grade III plus IV VGE was less in the bed rest group, and it took longer before Grade III and IV VGE were first detected [111]. As astronauts sometimes fly in commercial airliners or the T-38 jet shortly after training in the NBL, Test 10 included a hyperbaric and then a hypobaric exposure to evaluate the consequences of flying after diving under NASA specific training conditions.
---
## Table 1: Summary of DCS and VGE occurrence in hypobaric Tests from 1982-2015

| Test      | P2 (psia) | Conditions    | Subjects<br/>m | f  | Mean Age (yrs) | DCS | VGE (any Grade) | VGE (Grade IV) |
| --------- | --------- | ------------- | -------------- | -- | -------------- | --- | --------------- | -------------- |
| 1a        | 4.3       | P             | 11             | 0  | 34.5           | 4   | 7               | 4              |
| 1b        | 4.3       | S             | 13             | 0  | 32.3           | 3   | 11              | 7              |
| 1c        | 4.3       | S             | 12             | 0  | 32.0           | 4   | 7               | 6              |
| 1d        | 4.3       | S             | 3              | 0  | 39.6           | 2   | 3               | 2              |
| 2a        | 4.3       | P             | 23             | 0  | 31.6           | 7   | 15              | 8              |
| 2b        | 4.3       | S             | 22             | 0  | 31.5           | 6!  | 10              | 7              |
| 3a        | 4.3       | P             | 28             | 0  | 31.0           | 6   | 13              | 11             |
| 3b        | 4.3       | P,S           | 35             | 0  | 30.1           | 8   | 20              | 8              |
| 3c        | 4.3       | P             | 14             | 0  | 32.5           | 3   | 5               | 1              |
| 3d        | 4.3       | P,S           | 12             | 0  | 28.5           | 2   | 5               | 2              |
| 4a        | 4.3       | P,S           | 12             | 0  | 30.1           | 1   | 7               | 3              |
| 4b        | 4.3       | P,S           | 12             | 0  | 30.1           | 0   | 2               | 1              |
| 4c        | 4.3       | P,S           | 12             | 0  | 30.1           | 0   | 4               | 1              |
| 4d        | 4.3       | P,S           | 12             | 0  | 30.1           | 0   | 0               | 0              |
| 4e        | 4.3       | P,S           | 12             | 0  | 30.1           | 0   | 4               | 1              |
| 4f        | 4.3       | P,S           | 12             | 0  | 30.1           | 0   | 0               | 0              |
| 5a        | 4.3       | P             | 19             | 19 | 31.5           | 4   | 11              | 4              |
| 5b        | 4.3       | P             | 11             | 0  | 32.0           | 0   | 0               | 0              |
| 6         | 6.0       | S             | 15             | 14 | 32.9           | 1   | 3               | 0              |
| 7a        | 6.5       | direct ascent | 11             | 0  | 28.2           | 4!! | 8               | 6              |
| 7b        | 6.5       | direct ascent | 11             | 0  | 28.2           | 2   | 8               | 4              |
| 8a        | 6.5       | direct ascent | 29             | 11 | 32.5           | 7   | 20              | 13             |
| 8b        | 6.5       | direct ascent | 30             | 11 | 32.6           | 10! | 22              | 17             |
| 9a        | 6.5       | direct ascent | 15             | 9  | 32.1           | 1   | 12              | 7              |
| 9b        | 6.5       | A             | 14             | 9  | 33.8           | 2!  | 6               | 1              |
| 9c        | 4.3       | A             | 9              | 2  | 34.8           | 3   | 5               | 4              |
| 9d        | 4.3       | A             | 6              | 1  | 36.4           | 0   | 2               | 0              |
| 9e        | 4.3       | E,A           | 7              | 0  | 34.6           | 0   | 2               | 0              |
| 10        | 10.1      | FAD           | 14             | 5  | 31.7           | 1   | 6               | 3              |
| 11a       | 4.3       | P,A           | 16             | 12 | 33.2           | 3   | 9               | 4              |
| 11b       | 6.5       | direct ascent | 1              | 3  | 39.5           | 0   | 1               | 0              |
| Phase I   | 4.3       | P,E,S,A       | 33             | 14 | 29.1           | 9   | 23              | 2              |
| Phase II  | 4.3       | P,E,S,A       | 35             | 10 | 31.7           | 0   | 14              | 3              |
| Phase III | 4.3       | P,E,S,A       | 8              | 1  | 29.9           | 2!  | 1               | 1              |
| Phase IV  | 4.3       | P,E,S,A       | 44             | 12 | 30.1           | 8   | 23              | 7              |
| Phase V-1 | 4.3       | P,E,A         | 7              | 2  | 31.5           | 3   | 5               | 2              |
| Phase V-2 | 4.3       | P,E,A         | 1              | 2  | 39.2           | 1!  | 3               | 2              |
| Phase V-3 | 4.3       | P,E,A         | 38             | 10 | 36.9           | 7   | 25              | 5              |
| Phase V-4 | 4.3       | P,E,A         | 3              | 3  | 31.5           | 3   | 3               | 1              |
| Phase V-5 | 4.3       | P,E,S,A       | 37             | 11 | 32.3           | 2   | 14              | 8              |
| Nuc-1     | 4.3       | P,E,S         | 16#            | 5  | 36.4           | 4   | 13              | 6              |
| Nuc-3\*   | 4.3       | P,E,S         | 23             | 7  | 37.0           | 2   | 9               | 3              |

Conditions: P, some PB occurred before ascent; S, a portion of the PB was spent at 10.2 psia breathing 26.5% O₂; A, subjects were "adynamic" (no ambulation before or during the altitude exposure); E, a prescribed exercise was performed during some interval of the PB; FAD, flying after diving; ! One case was classified as Type II DCS; !! 2 were classified as Type II DCS; # One case of LVGE was removed early so total count for DCS is n=20; *as of 09/04/2015 since testing of Nuc-3 continues.
---
As part of the NASA Prebreathe Reduction Program (PRP), several trials evaluated the benefits of different exercise regimens during PB: short and intense, long and mild, and combinations of the two. The goal of PRP was to combine known factors that reduce the P(DCS), such as exercise and adynamia, with representative EVA work simulation in a PB protocol for ISS construction and maintenance. Avoiding ambulation during PB and at altitude does reduce the incidence of DCS and VGE in the lower body, so adynamia is included in all current validation testing as an analog to working in μG [66, 67, 112, 113], although there are contrary observations [114, 115]. In PRP Phases I through IV, researchers evaluated the influence of combined intense dual-cycle ergometry for 10 min with additional low-intensity exercise on the DCS and VGE outcome. After completing the initial 50 min PB at site pressure, the subjects were depressurized to 10.2 psia over 30 min while still breathing 100% O₂, and then 30 min were spent at 10.2 psia breathing 26.5% O₂ to reproduce the suit donning conditions in the ISS airlock. Then 100% O₂ was reintroduced into their masks, and they were repressurized to site pressure within 5 min to complete the final 35 min of PB. After a 150 min total PB time, a final depressurization from site pressure to 4.3 psia was completed in 30 min, and the subjects simulated EVA work tasks at 4.3 psia for 4 hr. Phase II met the accept conditions, as described earlier, for an ISS PB and became the operational Exercise PB protocol. In PRP trials from Phases V-1 to V-4, researchers evaluated whether mild exercise that could be performed during an in-suit PB at 14.7 psia would be effective, but none met the prospective accept conditions. The final trials in this series (Phase V-5) extended mild exercise and the total PB time to 190 min that included a 30-min suit donning step at 10.2 psia and became the operational ISLE PB protocol.

All tests under the PRP imposed non-ambulation during the PB and while at 4.3 psia, our analog of lower body activity in μG. However, exploration class EVAs will include significant ambulation on a planetary surface, so ambulation while at 4.3 psia without ambulation during the PB, designated nucleation 1 test (Nuc-1), and ambulation during the PB without ambulation at 4.3 psia, designated nucleation 3 test (Nuc-3), were evaluated with Phase II serving as the historical control (no ambulation during PB or while at 4.3 psia). The Nuc-3 trial summary findings were that DCS, VGE, and Grade IV VGE were significantly greater in Nuc-1 compared to Phase II control, indicating that ambulation during decompression is a major risk factor for DCS [116, 117]

## Exploration Atmosphere Human Testing

The 8.2psi / 34% O₂ Exploration Atmosphere PB human validation testing was started at JSC in 2022, with 6 subjects performing 5 simulated EVAs (30 total 'exposures') over an 11-day period (PB protocol: 20 min 85% O₂); 2 cases of DCS were observed in this initial test; however, additional testing is planned for 2023 to attain sufficient statistical significance.

Future testing will also explore alternate suit pressures (higher than 4.3psi), different prebreathe durations, and potentially alternate pressure/O₂ saturation points.

## Inadequate Denitrogenation

Much about denitrogenation and hypobaric DCS that was learned during and shortly after WW II is available on the pages of Fulton's 1951 book [3, 118], with additional information in the 4ᵗʰ
---
edition of *Fundamentals of Aerospace Medicine* [119] and from *The Proceedings of the 1990 Hypobaric Decompression Sickness Workshop* [120]. The advent of Doppler ultrasound bubble detection technology in the 1970s provided a significant tool to understand DCS. Clearly, denitrogenation protocols are effective in reducing the P(DCS) and the severity of symptoms, as well as the potential for VGE and arterial gas emboli (AGE). After denitrogenation, which typically uses oxygen (O₂) prebreathing, an astronaut has a smaller amount of tissue nitrogen (N₂) to manage. Once the astronaut depressurizes to a low-pressure spacesuit, the volume expansion (per Boyle's Law) of this remaining N₂ at the new lower pressure is concerning.

One major contributor to how much N₂ stays in the body after a PB is body fat content. It is important to define the minimum PB time that protects the greatest number of EVA astronauts, given a reasonable range of body types. In addition, PB procedures must be simple and balance the risk of DCS with available treatment resources [121]. Risk is defined as the P(DCS) and the consequence of DCS, and since the consequence of a serious case of DCS in space is high, then the P(Serious DCS) must be very low to achieve an acceptable operational risk.

Males and females each display a wide range of body types. A brief generic comparison using gender illustrates that no two people have the same quality or quantity of N₂ elimination (wash-out) and uptake (wash-in). Table 2 shows the estimated volume of N₂ dissolved in lean and fat tissues in a representative male and female. The total volume of N₂ is slightly more in the woman than the man, given an N₂ solubility coefficient of 0.0146 ml (STPD) N₂/ml tissue • ATM N₂ in lean (aqueous) tissue and 0.0615 ml N₂/ml tissue • ATM N₂ in fat (lipid) tissue as well as other factors.

**Table 2: Estimated N₂ Content by Gender**

| Gender | Weight (kg) | body fat (% total wt) | fat mass (kg) | N₂ volume in fat (ml)\* | lean mass (kg) | N₂ volume in lean (ml) | Total N₂ volume (ml) |
| ------ | ----------- | --------------------- | ------------- | ----------------------- | -------------- | ---------------------- | -------------------- |
| Male   | 75          | 10                    | 7.5           | 405                     | 67.5           | 778                    | 1183                 |
| Female | 60          | 25                    | 15.0          | 809                     | 45.0           | 519                    | 1328                 |

\* Density of fat = 0.9 g/mL, Density of lean tissue = 1.1 g/mL, partial pressure of N₂ = 0.79 atmospheres absolute (ATA) in breathing air, and total body weight was not reduced to compensate for the weight of inert bone.

Apparent in this example is that the amount of N₂ in fat tissues of woman is twice that compared to men and that the amount of N₂ in lean tissues of men is slightly greater compared to woman. Given enough PB time, the same total volume of N₂ would be removed from both genders. However, as PB time is always limited, the kinetics of N₂ elimination and the relative contributions
---
of N₂ from fat and lean tissues during a limited PB must be considered. For example, a large amount of N₂ would be quickly eliminated from the well-perfused and large lean tissue reservoir, with a lesser amount of N₂ coming from the poorly perfused fat depot. The poorly perfused fat contributes some N₂ throughout the PB, but is likely responsible for the long tail of a typical N₂ elimination curve. In females, a large amount of N₂ is initially removed from the well-perfused lean tissue reservoir, with a greater amount of N₂ typically coming from the poorly perfused fat depot compared to men. The poorly perfused fat tissue has 5 times greater affinity for N₂ than does the well-perfused lean tissue. As a result, a large amount of N₂ is available from fat tissue in woman, and the N₂ slowly leaves the body during PB, so that you would expect an even longer tail on a typical N₂ elimination curve for women compared to men, however, this depends on individual body types.

## *Air Break during Prebreathe*

Various methods to preserve the quality of and confidence in a PB protocol during transition from the mask to the suit have been evaluated at JSC, and all were found to be inadequate. In effect, the inability to avoid a potentially long air break in PB at 14.7 psia and ignorance of the consequences of an air break during PB were responsible for the development of the staged denitrogenation protocols on the Shuttle and ISS [29, 95]. There are relatively few research studies that studied air break in PB [118, 122-128].

A lengthy break in PB is an operational reality that could compromise an otherwise safe denitrogenation procedure and jeopardize a scheduled EVA. The NASA Aeromedical Flight Rules define O₂ payback time based on the location and duration of a simple air break during a PB. Payback time is the number of min of additional PB time needed to compensate for an interruption in the original PB time. For air breaks during resting PB, the payback time on 100% O₂ is 2x the duration of the air break, and 4x the duration if the air break occurs early in the Exercise PB protocol for the ISS. A break in PB longer than 10 min requires that the PB be repeated from the start, or that the crew switch to an alternative PB protocol. A notable case of a complicated break in PB occurred during the preparations for the second of 3 EVAs on STS-129. A mechanical problem in the airlock control panel on the ISS occurred about 2 hr into the sleep period of the campout PB. This failure initiated a repressurization of the airlock. There was no reasonable recovery from this air break due to the time needed to reconfigure the airlock operations. The decision was made to switch to Exercise PB, which was completed the following day and preserved the original scheduling of the second EVA.

Estimates for PB payback time have ranged from 1x [123] to 35x [124] the duration of the air break. Unfortunately, no published results exist that can be confidently applied to NASA operations. In addition, there are no data about payback time if PB is interrupted during exercise. Simple rules for PB compensation after an air break are desirable for spaceflight EVA operations, but no two people have identical N₂ uptake and elimination kinetics, and in reality, the duration of the break, the point at which the interruption in the PB occurred, and the remaining amount
---
of PB time are infinitely variable. Breathing 1 ATA (14.7 psi partial pressure) of O₂ is known to decrease cardiac output and to increase peripheral vascular resistance by increasing vasoconstriction [129, 130]. It is reasonable to suppose asymmetrical N₂ kinetics as a consequence of an air break and that there is a change in the size distribution of tissue micronuclei as a function of the O₂ window during the PB [131], and the size distribution is influenced by air breaks. Thus, simple payback rules may not suffice under all conditions, rather a quantitative approach to assess payback time is needed [132]. Data from Pilmanis, et al. [128], 2010 showed that a 10 min air break, 30 min into a 60 min PB prior to a 4.37 psia exposure reduced the mean time to onset of symptoms yet increased DCS incidence at 1 hr exposure compared to controls.

## *Hypobaric Ascent Limit*

The need for high-altitude bombing during WW II and the rapid advancement in jet engine development after the war put aviators at risk for DCS, hypoxia, and hypothermia until pressurized and air-conditioned aircraft cabins became common. Before these technical advances occurred, researchers in Canada and the U.S. characterized DCS, mostly with young airmen in training, using hypobaric chambers [3, 133, 134]. It was quickly realized that the altitude, the time spent at altitude, and exercise at altitude increased the risk of DCS, both pain only DCS and serious DCS linked to reactions in the cardiovascular and nervous systems [40, 135]. Such provocative testing will likely never be performed again with human subjects and "modelers" of DCS must be content with these data to define the upper range of dose-response curves.

Denitrogenation with enriched O₂ mixtures dramatically reduced both pain only and serious DCS, and most fit, young men could tolerate a degree of depressurization even without the benefit of a PB. During the war years, the criteria for a successful ascent centered around having enough time to perform the mission before DCS symptoms became debilitating. Under these extreme conditions, ascents to 6,096 - 7,620 m (20,000 - 25,000 ft) were acceptable in most operational settings. Several studies were initiated to identify and screen out personnel who were potential "weak links" as a means to reduce operational impacts of DCS on the mission. These efforts were abandoned as ineffective and costly but highlighted the reality of both between and within subject variability to DCS. As the interest in aviator DCS increased after WW II, primarily through the United States Air Force (USAF) and NASA, a systematic approach led to a better understanding of hypobaric ascent limit. Also, a shift in thinking from "tolerable" symptoms to the first onset of mild symptoms reduced the threshold altitude for DCS.

Each year, millions of people on commercial flights are quickly exposed to between 1,829 - 2,438 m (6,000 - 8,000 ft) altitude for long periods. Most barophysiologists would agree that a rapid ascent to 3048 m (10,000 ft) does not induce significant risk of DCS, but hypoxia soon limits useful physical activity. The use of enriched O₂ at higher altitudes confounds the basic question about the DCS limit to direct ascent on air [136]. In addition to defining the threshold of evolved gas
---
and the interaction of the evolved gas with living tissues that produce symptoms, there are practical reasons to define a hypobaric ascent limit. Prebreathing takes time and resources, and a spacesuit pressurized greater than the lowest pressure to cause VGE and DCS could be an option to eliminate the risk of DCS[137].

Work to define the threshold for a no PB spacesuit suggests that 4,420 m (14,500 ft) altitude is close to a no-DCS ascent, with VGE still produced at an altitude of 3,505 m (11,500 ft) [42]. Webb, et al. [138] showed that a spacesuit at 9.5 psia (11,500 ft) prevented DCS during 5 repeated exposures in 22 subjects. There is some threshold below which the gas that is evolved after depressurization is insufficient to elicit symptoms, even if it is difficult to establish this without exception. Table 3, modified from Conkin, et al. [42], lists hypobaric exposure pressures and the associated DCS and VGE incidence.
---
## Table 3: Studies Implemented to Define Threshold Altitudes for DCS and VGE

| P1N₂ / P2        | P2 (psia) | DCS cases / n | VGE cases / n | Reference(s)             |
| ---------------- | --------- | ------------- | ------------- | ------------------------ |
| 1.49, day 1 of 3 | 7.8       | 2 / 64 = 3.0% | 28 / 64 = 43% | \[42, 139, 140]          |
| 1.43, day 2 of 3 | 7.8       | 2 / 62 = 3.0% | 29 / 62 = 46% |                          |
| 1.42, day 3 of 3 | 7.8       | 1 / 60 = 1.6% | 25 / 60 = 41% |                          |
| 1.40             | 8.3       | 1 / 31 = 3.2% | 8 / 31 = 26%  | \[141, 142]              |
| 1.36             | 8.5       | 0 / 9 = 0%    | 3 / 9 = 33%   | USAF pilot study\*,\[42] |
| 1.29             | 9.0       | 0 / 16 = 0%   | 7 / 16 = 43%  |                          |
| 1.22             | 9.5       | 0 / 6 = 0%    | 1 / 6 = 17%   |                          |
| 1.22             | 9.5       | 0 / 31 = 0%   | 8 / 31 = 26%  |                          |
| 1.22, day 1 of 5 | 9.5       | 0 / 23 = 0%   | 0 / 23 = 0%   | \[42, 138, 143]          |
| 1.11, day 2 of 5 | 9.5       | 0 / 22 = 0%   | 0 / 22 = 0%   |                          |
| 1.10, day 3 of 5 | 9.5       | 0 / 22 = 0%   | 0 / 22 = 0%   |                          |
| 1.10, day 4 of 5 | 9.5       | 0 / 22 = 0%   | 0 / 22 = 0%   |                          |
| 1.10, day 5 of 5 | 9.5       | 0 / 22 = 0%   | 0 / 22 = 0%   |                          |
| 1.16             | 10.0      | 0 / 8 = 0%    | 2 / 8 = 25%   | USAF pilot study\*\[42]  |

*USAF pilot studies using subjects with history of DCS and VGE.

Kumar, et al. [144] and Webb, et al. [145] summarized the information in Table 3 and other information about altitude threshold, however, came to different conclusions. Kumar stressed that any threshold for symptoms is conditional on other factors, with his lowest conditional threshold defined as 3,353 m (11,000 ft) altitude. Webb reported about 5% DCS for 6,096 m (20,000 ft) altitude. Probing for the least amount of decompression dose to elicit symptoms is a difficult task since there are always exceptions to the rule [146, 147].

## Activity during EVA

No single variable, other than O₂ PB time, has more of an impact on the P(DCS) than exercise at altitude. Cook [148] summarized the importance of exercise at altitude as a factor to increase the incidence, the severity, and shorten the latency time to the first report of DCS. One can limit the P(DCS) at a given suit pressure by limiting exercise during EVA, but this is impractical in most applications since astronauts are performing physical tasks during an EVA. The general approach is to provide sufficient PB so that the type, intensity, and duration of EVA work are not considerations. There is evidence though that the peak exercise loads may be the primary determinant of exercise impact on DCS risk[113, 149]. Importantly, ambulation that stresses the knees and ankles on the surface of the moon or Mars is expected to increase the risk of DCS for any PB protocol that is otherwise performed well in μG [67, 113, 150].
---
Figure 4 is a classic presentation of the importance of exercise type and intensity toward the P(DCS). The figure is redrawn from Henry [151]. It shows the rate of DCS as a function of lower body exercise intensity during a stair-step challenge.

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ```
3.5 |
|
3.0 |        *****
|       *     *  2X standard exercise
2.5 |      *       *       (88% after 1.5 hrs)
|     *         *
2.0 |    *           *
|   *             *
1.5 |  *               *    standard exercise
| *                 *          (78% after 1.5 hrs)
1.0 |*                   ****
|                        ****  1/3 standard exercise
0.5 |                            ****    (60% after 1.5 hrs,
|                                ***** 83% after 3 hrs)
0.0 +----+----+----+----+----+----+----+----+----+
0   10   20   30   40   50   60   70   80   90
time (min)
``` |

Figure 4: The rate of DCS as a result of exercise after an ascent to 3.0 psia without PB. Standard exercise was defined as 10 step-ups on a nine-inch stool in 30 sec, repeated at 5 min intervals.

## *Exercise Effects on Micronuclei*

The previous discussion focused on reducing the amount of tissue N₂ to limit bubble growth, the classic Haldanean approach, but an emerging area of DCS prevention is to also hinder the transformation of tissue micronuclei into growing bubbles [8, 9]. The presence of gaseous micronuclei in the tissues permits DCS under modest depressurizations [10]. Information about and evidence for tissue micronuclei come mostly from indirect observations. One consistent inference from these studies is that normal activity establishes a size distribution of micronuclei within tissues, which can then be modified by changing the type, timing and intensity of activity.

If micronuclei are considered and if the results from research on DCS are then applied to astronauts who perform EVAs, then walking in an altitude chamber is not a reasonable analog to EVA or "space walking" [66, 112, 152]. Exercise during depressurization increases the risk of DCS, generally in the limb performing the exercise [148, 150, 151, 153]. Walking is such a natural event that in research on DCS it is frequently ignored as being exercise. This simple and ubiquitous act has new relevance as humans venture into space and when they ambulate on the Moon and later Mars, especially as it relates to the risk of DCS. Calling an EVA in μG from the Shuttle or ISS a 'spacewalk' is a misnomer. Astronauts do not ambulate in the conventional sense but rather anchor their legs to a stable structure so that the upper body can effect some task. Powell coined the term "adynamia" to characterize the lack of movement and, therefore, the
---
lack of dynamic forces in the lower body (lower body adynamia) over several days of adaptation to μG and during EVAs [29, 67, 111, 154].

The fundamental premise of adynamia is about the control of nucleation processes within tissues and fluids. In the absence of supersaturation, the spontaneous rate of nucleation is inconsequential when micronuclei on the order of microns in radius are considered. However, the number or distribution of micronucleus sizes can be influenced before supersaturation exists when mechanical energy is added to the system. It is notable that subjects who performed brief but vigorous dual-cycle (arm and leg) ergometry at the start of an exercise PB showed earlier VGE onset compared to those who performed the ergometry about 15 min into the start of the PB [76]. A 15 min delay in starting the ergometry in a 150 min total PB time delayed VGE onset time in research subjects during a subsequent exposure to 4.3 psia. Astronauts always perform EVAs in pairs. So those that use the Exercise PB protocol start the PB at the same time, but someone must go first since there is only one leg ergometer on the ISS dedicated to this protocol.

Violent muscular contractions in bullfrogs before a hypobaric exposure [155] were associated with bubble formation in the resting animals while at altitude. The number of bubbles was reduced when the frogs were allowed to recover for as long as 1 hr after electrical stimulations. The authors offered 2 explanations: a short-lived local increase in carbon dioxide (CO₂) that facilitated bubble growth at altitude, or the inception of micronuclei or some other short-lived entities that would later facilitate the growth of bubbles at altitude. This same concept was tested in humans [156] when 20 subjects were exposed to 6.2 psia on 3 separate and random occasions without the confounding of PB or any exercise at altitude during a 2 hr exposure. Each subject did 150 deep knee flexes in 10 min either 2 hr, 1 hr, or just before ascent, with the remaining time spent adynamic in a chair. It was hypothesized that exercise before decompression would generate a population of some entity (micronuclei, macronuclei, vapor-filled cavities trapped on vascular endothelium, or increase the concentration of CO₂) that would diminish in size or concentration given enough time before ascent. The investigators used subsequent VGE information to indirectly test the hypothesis. They observed that intense lower-body activity just before the altitude exposure did cause more VGE to appear and to cause them to appear earlier than when exercise was done earlier. The critical observation was that the predisposing factor(s) diminished with time while subjects sat quietly in a chair before the ascent.

If DCS outcome is related only to tissue N₂ supersaturation, then perhaps the decrease in P(DCS) tracks the decrease in computed supersaturation. If the relationship is not a mirror image, then perhaps factors other than N₂ supersaturation are co-responsible. The dashed line in Fig. 4 is from the natural logarithm transformation of the exponential decay in a 360 min half-time compartment normalized by dividing the initial tissue N₂ pressure by 11.6 psia, ambient pN₂ at sea level. The solid curve is the same transformation applied to the P(DCS) from a survival model (Conkin *et al.* 1996) evaluated over 6 hr of PB given that the person performed mild exercise at 4.3 psia for 4 hr while breathing 100% O₂ through a mask. Other factors that dictate the DCS outcome must exist besides tissue N₂ supersaturation, or the 2 plots would look similar. If DCS
---
outcome is a complex competition between the potential for evolved gas and the transformation of micronuclei into bubbles, then it might be expected that the curves for log[P(DCS)] and log(normalized N2 pressure) would diverge over a range of PB time.

The physics of micronucleus stability, creation, size distribution, absolute numbers in tissues, and transformation into growing bubbles for a given N2 supersaturation must be complex [157-159]. One could hypothesize that only a few large-radius micronuclei could be absorbed during a short, 100% O2 PB, and that more large- and small-radius micronuclei are absorbed after more than 90 min of PB. There would come a point during a long PB where fewer and smaller-radius micronuclei exist to subsequently transform into growing bubbles under the prevailing reduced N2 supersaturation, as suggested by the rapid decrease in ln[P(DCS)] after 3 hr of PB in the survival model (Figure 5). The reality of bubble growth in tissue is that it is not just the absolute potential for evolved gas, as reflected in an exponential washout curve, but it is a competition between the potential for available gas and the population of micronuclei that are available to accept the excess gas and transform into growing bubbles. The acceptance of this excess gas occurs through simple diffusion, but that is the only simple statement possible.

|                                                                                                                                                                                                                                                         |   |   |   |   |   |   |   |   |   |   |   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | - | - | - | - | - | - | - | - | - | - | - |
| LN normalized P1N2 and P(DCS)0.0 ┌─────────────────────────────────────────┐│ │-0.6 ├─ ││ │-1.2 ├─ ││ │-1.8 ├─ ││ │-2.4 ├─ ││ │-3.0 └─────────────────────────────────────────┘0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0 5.5 6.0prebreathe time (hrs) |   |   |   |   |   |   |   |   |   |   |   |

Figure 5: Change in computed tissue N2 pressure (dashed curve) and the P(DCS) (solid curve) as a function of PB time

The classic soda-bottle analogy of bubbles in the body illustrates the physical consequence of depressurization, but emerging science suggests that activation of various stress-induced biomolecules before, during, or after depressurization will influence the DCS and VGE outcomes [155, 160, 161]. Astronauts routinely take aspirin and other pharmacological agents to manage the stress and discomforts of space flight and EVAs, which may influence the DCS and VGE outcomes. The large surface area of the vascular endothelium and its interaction with stress-

38
---
induced biomolecules offers an opportunity to understand how excess intracellular dissolved gas becomes extracellular evolved gas bubbles that are then relocated to the lungs [162].

## Duration and Frequency of EVA

The evolution of gas in tissue is a time-dependent process. Nims [7] systematically describes the time-dependent process in the development of his theoretical model to describe aviator DCS. Gas evolution has a lag phase, a growth phase, and finally a recovery phase if the EVA continues since tissue and bubble N2 continues to be removed while breathing 100% O2 during the EVA. One can limit the P(DCS) at a given suit pressure by limiting the EVA exposure time, although this is impractical in most applications. The general approach to limiting P(DCS) is to provide sufficient PB so that EVA duration is not a consideration.

Figure 6 shows the distribution of symptom failure times from denitrogenation protocols that are considered conservative based on NASA PB validations. Symptom failure times are most likely 75 to 175 min in these data, with fewer cases appearing in minutes and other at 6 hrs. There is a period during any EVA, about 3 hrs, after which the likelihood is small that DCS will be reported. Again, this is attributed to the continued removal of N2 during an EVA.

|                                                                                                                                                               |   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | - |
| Count	Proportion per Bar&#xA;60	&#xA;50&#xA;40&#xA;30&#xA;20&#xA;10&#xA;0&#xA;0    50   100  150  200  250  300  350  400&#xA;time of first DCS symptom (min) |   |

Figure 6: Histogram distribution of time to reporting of 216 symptoms in 119 cases of DCS. Distribution is skewed right with largest number of reports at about 120 min into the hypobaric exposures.

Although EVA has historically been a single event in a flight day, that may not be the standard operational concept for future exploration missions. Development of the Exploration Atmosphere in combination with the use of suitports will allow for the possibility of multiple EVAs in a single day or at a minimum, the ability to perform EVAs multiple days in a row. Currently,
---
exploration design reference missions assume that all crewmembers can perform up to 24 hours of EVA per week. EVAs have historically been treated as a single isolated event in relation to management of DCS risk, but this will no longer be the case. Most evidence supports the idea that the use of frequent, shorter EVAs with intermittent recompression is likely to decrease overall DCS risk, but empirical testing followed by flight experience would be the preferred evidence base [109, 163-165].

## Physiological Predisposition and Risk of Decompression Sickness

It has been observed that some divers and aviators are particularly resistant or susceptible to DCS and VGE [80, 166, 167]. Depressurization schedules developed to protect the most susceptible are then ultra-safe for the resistant, and therefore not efficient. There is a long history of persistent efforts to identify those who are susceptible, and to identify the physiological and anatomical factors associated, as either a cause or a correlate, with susceptibility [106]. Selection schemes, except for natural selection, have not developed past the conceptual stage primarily because prospective, well-controlled studies with adequate sample size are expensive.

Table 4 lists examples of factors associated with risk of DCS and the associated references. Any global conclusions on individual factors are confounded by inconsistencies in the DCS mitigation strategy (primarily PB duration) and decompression dose and duration. Law and Watkins [168] reviewed literature on individual susceptibility to DCS but provided no additional recommendations for astronaut screening and did not refute the current practice of eliminating astronaut candidates due a flow-significant atrial septal defects.

### Table 4: Individual Factors Associated with Risk of DCS and VGE

| Factor Associated with Risk of DCS and VGE | Reference(s)             |
| ------------------------------------------ | ------------------------ |
| Age                                        | \[79, 81, 169-172]       |
| Patent Foramen Ovale                       | \[173, 174]              |
| Gender                                     | \[26, 77, 175, 176]      |
| Menstrual Cycle Time                       | \[175, 177]              |
| Aerobic Fitness                            | \[78, 80, 175, 178, 179] |
| Body Fat                                   | \[175, 180]              |
| Hydration Status                           | \[181]                   |

One challenge to understanding the contribution of the factors laid out in Table 4 to DCS and VGE outcomes is that all are just part of a large system and it is difficult to isolate the contribution of 1 factor. In reality, DCS and VGE outcomes are multifactorial and confounded by many factors, particularly the decompression dose [111].
---
A practical approach, given a large sample of quality research results, is to perform a multivariate statistical analysis in which the uniqueness of each trial becomes part of the reason, along with other explanatory variables, for the outcome. In other words, a multivariate analysis such as logistic regression or survival analysis identifies and controls for confounding and interacting variables so that a better interpretation of the outcome is possible [76, 182]. Although a multivariate analysis with large numbers of quality research data with an appropriate range of explanatory variables is necessary to assign the appropriate contribution to an explanatory variable, in general, this approach has not been used, and contributes to contradiction and confusion in the literature.

With limited objective data to support specific recommendations for astronaut selection and preparation, we are left with suggesting that an astronaut should be adequately hydrated prior to EVA and that increased aerobic fitness and lower body fat levels may contribute slightly to decreased DCS risk.

## Relationship between VGE and Hypobaric Decompression Sickness

Ever since silent bubbles were associated with modest hyperbaric and hypobaric exposures, there has been a vigorous debate about the value of VGE detected in the pulmonary artery or other veins to predict subsequent DCS outcome [183]. The fact that bubbles are present without overt symptoms suggests that, at best, the presence of VGE is a necessary but not sufficient condition for DCS, and relationships between the two are correlative as opposed to cause-and-effect. Correlative relationships differ from one study to the next depending on many factors: such as the decompression dose and the type of breathing gas [136, 184]; the type of ultrasound equipment, training of the Doppler technician, and the methods used to quantify the Doppler signals, [e.g., simple bubble grades or more sophisticated "time-intensity" approaches] [185]. However, the absence of VGE is strongly associated with the absence of DCS.

The positive and negative predictive values of VGE have been explored in both divers and aviators [71, 167, 183, 186]. The desire to have a single global understanding about the relationship between VGE and DCS is frustrated because of differences in bubbles between divers and aviators, and even differences attributed to gender[77]. Trials that produce Grade IV VGE in 50% of divers will never be sanctioned since this would result in an unacceptably high incidence of DCS, as well as a high incidence of serious DCS. But Grade IV VGE are routinely assigned in hypobaric depressurizations, even after conservative PBs [88]. DCS incidence on the order of 20% is common, with only about 1% of all exposures resulting in serious DCS in NASA testing and a higher percentage in tests of protocols for the USAF [187]. Divers returning to 1 ATA from a provocative SCUBA dive may produce many small bubbles, predominately composed of N2. In contrast, aviators may produce fewer large bubbles composed of as much as 70% metabolic gases [188-190]. Since the gas composition of VGE in divers and aviators is different, then it is reasonable to expect that the association between VGE and DCS reflect this difference. In summary, a global understanding about the relationship between VGE and DCS is not yet
---
available. The absence of this understanding results in contradictions when the experiences of divers and aviators are compared.

It is more than coincidental that VGE are often detected in high intensity coming from a region of the body where a sign or symptom may appear. Table 5 shows that the positive predictive value for DCS of any VGE grade or of Grade III and IV is only 32 or 39% [70]. Someone with prior knowledge of even Grade IV VGE from a particular limb in an aviator is less than 40% confident that a DCS symptom will follow. The absence of VGE has a negative predictive value of 98% in these data, but much less in other hypobaric data [191-193]. So, it is more informative to know that an aviator or astronaut has no VGE in the pulmonary artery if the goal is to predict a subsequent DCS outcome [194].

**Table 5: Measures of Association Between VGE and DCS**

|                    |                               |                                   |
| ------------------ | ----------------------------- | --------------------------------- |
| Measure            | Grades 0 – IV<br/>(n = 1,322) | Grades 0, III, IV<br/>(n = 1,210) |
| Sensitivity        | 0.922                         | 0.917                             |
| Specificity        | 0.718                         | 0.787                             |
| + Predictive value | 0.323                         | 0.391                             |
| - Predictive value | 0.980                         | 0.980                             |

Even though a one-to-one cause-and-effect relationship between VGE and DCS does not exist, there is a consistent temporal association between VGE and DCS. Figure 7 shows this temporal pattern. Not everyone who has VGE has subsequent DCS, and a few who do not have VGE do have DCS. The caveat here is that a similar VGE onset and recovery pattern is present in those who do and those who do not develop DCS. Any association between VGE detected in the pulmonary artery and pain only DCS in a distant limb is subtle.
---
## Figure 7: Time of VGE and DCS onset in 78 exposures with both VGE and DCS present (solid curve) and in 150 exposures with VGE only (dashed curve). The curves, all of which are skewed to the right, are the best-imposed normal distributions on histograms.

|                                                                                                                                                                                                                                                                                                                                                                    |   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | - |
| ```
Count
30|
27|        /--\
24|       /    \
21|      /      \
18|     /        \
15|    /   VGE    \
12|   /           \    DCS
9|  /             \      /\
6| /               \    /  \
3|/                 \__/    \___
0|___________________________________
0  25 50 75 100 125 150 175 200 225 250 275 300
DCS and VGE onset time (min)
``` |   |

The NASA Hypobaric Decompression Sickness Database contains 78 subjects with DCS onset times associated with 78 VGE onset times, with a mean TR of 1.67 ± 0.15 SD. Mean DCS onset time was 120 min ± 71 min SD and mean VGE onset time was 72 ± 55. In 150 other exposures, VGE were not associated with a report of DCS. The 150 exposures with VGE but without DCS had a mean VGE onset time of 90 ± 65 min and mean TR of 1.65 ± 0.19. The mean VGE onset time for all 228 exposures with VGE was 84 ± 62 min. Only 4 subjects had DCS without VGE being detected. The majority of exposures, a total of 317 out of 549 (57.7%), had no DCS or VGE, since the goal was to validate only safe PB protocols. The same pattern held for exercise during PB, but the incidence of DCS given that VGE were present decreased slightly from 14% to 11%. It was likely, but not certain, that an individual would report a DCS symptom after VGE were detected if they were detected early in the altitude exposure, if the intensity or grade of VGE from a limb region increased rapidly, and if the intensity or grade of VGE remained high [70, 71].

It is appropriate here to speculate on why VGE detected in the pulmonary artery seem disconnected from the DCS outcome even when the VGE seem to originate from a limb region. VGE moving in the venous blood and detected at a common location for all of the cardiac output are far removed from the site of bubble formation, so there is no guarantee that other tissues, such as fat and skin, do not contribute VGE to the venous return. There is no a priori reason why VGE cannot be produced in a limb region even if the critical volume of evolved gas needed to evoke a symptom has not been reached. Excess dissolved N₂ in muscles, tendons, ligaments, joints, cartilage, and other tissues can form bubbles in these tissues and can also diffuse into the low-pressure venous return where bubbles grow from micronuclei clinging to the vascular
---
endothelium. They accumulate, grow, and then pinch off and coalesce, to be carried with the venous return as muscle contractions "milk" the blood and bubbles into the venous return. So, it is understandable that VGE detected in the pulmonary artery are only indirectly linked to DCS symptoms. But even a weak association is helpful to visualize the primary cause of a symptom at a distant location and to visualize the transport of excess N₂ as bubbles. Advances in ultrasound technology will soon replace speculation with clear visual evidence of stationary bubbles growing within tissues and on the vascular endothelium.

It is preferable from a DCS standpoint to not have circulating VGE, with or without a PFO. Blood is a complex fluid, and the blood-endothelial interface forms a complex homeostatic surface, so the presence of bubbles in blood and at the blood-endothelial interface could be problematic. Aviators and astronauts share one feature with divers, healthy lungs that provide an efficient filter for VGE [195]. But aviators and astronauts are not immune from the consequences of embolic overload, even in healthy lungs. Many factors in the aerospace environment compromise healthy lung function. These factors combined with too many bubbles entering the pulmonary circulation can put this group at high risk [192]. Beyond the lungs, circulating emboli may also impact other areas of the body which are well perfused. The following describes a few topics of interest that are present due to decompression stress even without symptoms of clinical DCS.

## *In-suit Doppler Effort*

Monitoring for VGE in the pulmonary artery as the entire right-heart cardiac output enters the pulmonary circulation is the simplest approach for an unbiased assessment of the effective decompression dose, even if VGE are not directly linked to subsequent DCS. Noninvasive Doppler ultrasound bubble detection technology quickly advanced in the mid-1970's to where small, battery-operated devices were safe to use in operational settings. Investigators at Brooks AFB in the early 1980's proposed that a 5 MHz continuous wave bubble detector with simple analog recording be interfaced with the U-2 aircraft pressure garment. But scientific rationale and engineering capability were not enough to implement this system, even as a research tool. The idea was valid, and the rewards were great, so efforts persisted at JSC to provide an automated venous blood bubble monitor for use in the EMU. Several prototypes were developed and tested at JSC. A parallel effort was also initiated by the Russians, who eventually monitored subjects in the *Orlan* suit during altitude chamber flights.

The ability to acquire a stable, quality blood flow signal was verified during brief periods of μG during parabolic flight. The viscera within the chest stabilized in μG which allowed for good signal quality even under modest body motion [196] (Hadley *et al.* 1984). Technical advances continued, especially in the design of the probe. The final configuration was a triangular flat probe head with 1 transmit and 3 receive sensors spaced so that a rib was always spanned regardless of the probe orientation on the chest over the pulmonary artery. The sensor had to perform in a "hands off" operation once the EMU was donned. Various taping and strapping
---
options were evaluated to maintain orientation of the probe. Techniques to maintain the ultrasound coupling between the sensor and skin were needed since one hour of use in a hypobaric environment would evaporate the ultrasound gel. Issues of suit fit with the Doppler device inside the EMU were evaluated during normal training activities at the NBL. A final design emerged where the battery module, 2.4 MHz continuous wave ultrasound electronic module, and digital recorder module were separate on a belt worn around the waist. The system was flown on STS-87 and worn by Winston Scott while in the Shuttle, not in the EMU. The system was evaluated at 6.5 psia on 4 subjects in an altitude chamber (Test 11b), and recorded VGE in 1 subject. Finally, the system was used in the underwater habitat *Aquarius* where astronauts on the NEEMO 5 mission wore the unit for several hours after returning from dives deeper than the 56 feet sea water (FSW) saturation depth of the habitat. A significant finding was the recording of false positive VGE signals. Gas entrained by swallowing liquids was detected due to the proximity of the sensor to the esophagus [197]. This was significant since astronauts are encouraged to drink water from a 32-ounce drink bag within the EMU during long EVAs. The Doppler device, training, and use of the device under real world conditions was successful.

Despite a successful research and development program for an automated in-suit bubble detector a final operational system did not materialize. Safety concerns about the battery-operated device within the 100% O₂ EMU environment halted the effort and prevented exposure of an astronaut to 4.3 psia while shirtsleeve in the Shuttle or ISS airlock to evaluate the device. There was also an understandable resistance to implement this system out of concerns that the results could impact future EVA assignments.

## Modeling Evidence – Decompression Sickness

Probability models are critical to the understanding and mitigating DCS risk. These models are first developed as statistical descriptions of DCS incidence from a given data set and eventually predict DCS incidence effectively over a given boundary of input parameters. Certain DCS models will be described in the section and Appendix A is provided for a comprehensive summary of DCS model details. Models are typically used to develop potential PB protocols, which are then tested on the ground in hypobaric EVA simulations to ensure that the protocol achieves acceptable DCS risk level. DCS models assess impacts to ground validated protocols which are often modified during the transition from research to operations. In these cases, the models are used to ensure that changes to the validate protocol are neutral or in favor of enhanced crew safety. In some cases, DCS probability models, in conjunction with expert opinion, have been used in place of ground testing to accept a PB protocol, which was the case with the Campout PB.

In addition to statistically driven probability model, a decompression dose can also be computed from a biophysical model about bubble growth, such as the maximum size a theoretical bubble achieves, the rate of growth of the bubble, or the summed volume from a collection of bubbles competing for inert gas [8, 198].
---
## Tissue Ratio

Fundamental to understanding the P(DCS) in astronauts is to first understand how we calculate a tissue ratio (TR). TR is a simple index of decompression dose, first used by Haldane to define the limit to direct ascent for divers at the end of the 19$$^{th}$$ century. The reader is referred to Stepanek and Webb [119] for the historical background on TR.

TR is the ratio of computed P1N$$_2$$ in a theoretical tissue to ambient pressure. Equation 2 defines P1N$$_2$$ and P2 is the ambient pressure after depressurization. Prebreathing 100% O$$_2$$ or O$$_2$$-enriched mixtures before a hypobaric exposure reduces P(DCS), so it is necessary to account for the use of O$$_2$$-enriched mixtures as part of the expression for decompression dose. After pN$$_2$$ in the breathing mixture changes, such as during a switch from ambient air to a mask supplied with 100% O$$_2$$, the pN$$_2$$ that is reached in a designated tissue compartment after a specific time is P1N$$_2$$:

$$P_1N_2 = P_0 + (P_a - P_0)(1 - e^{-kt})$$        (Equation 2)

where P$$_1$$N$$_2$$ is calculated for the tissue after t min, P$$_0$$ is the initial pN$$_2$$ in the compartment, P$$_a$$ is the ambient pN$$_2$$ in the breathing mixture, and t is the time at the new P$$_a$$ in min. The tissue rate constant k is equal to $$\frac{ln(2)}{t_{1/2}}$$, where t$$_{1/2}$$ is the half-time for pN$$_2$$ in the 360 min compartment. The particular half-time compartment is a statistical construct that optimizes TR as decompression dose to the observed dichotomous DCS or VGE outcomes from a collection of trials [199]. Different half-time compartments reflect the varying rates at which different body tissues take up and eliminate inert gases. For example, fast 5- and 10-minute half-time compartments are used to represent the brain and spinal cord, which are highly perfused and rapidly take-up and eliminate inert gases. A long 360 min half-time is associated with long PB times tested by NASA [70]. A shorter half-time combined with long PBs produce low TRs that are not consistent (optimized) with trials that yield significant DCS and VGE incidence. The half-time compartment is simply a surrogate linked to the actual process at the tissue level that dictates the true evolved gas condition.

Equation 3 describes the simple case where P$$_a$$ changes instantaneously, a step-change. This form is sufficient in most applications since donning or removing an O$$_2$$ mask changes P$$_a$$ within a few breaths. There is also the possibility that P$$_a$$ changes through time, such as breathing air during a long depressurization, or changing the N$$_2$$ content through time at some intermediate pressure. An expanded form of Eq. 3 covers these cases. One novel application is to reduce N$$_2$$ content through time as dictated by the operational timeline such that P1N$$_2$$ is appropriate at the time of suit donning, thus avoiding a final in-suit PB period. This application requires an automated control system to change the breathing atmosphere through time and space within a vehicle that is compatible with enriched O$$_2$$. The cost likely exceeds the rewards with this approach, so it has not been pursued. Finally, Eq. 2 is modified to compute P1N$$_2$$ to account for intervals of exercise during PB. The tissue rate constant k is defined in terms of %VO$$_2$$ peak during the PB (Conkin et al. 2004).

46
---
Equation 3 is one form of TR as decompression dose, which approximates the potential volume at ambient pressure of N₂ evolved in a unit volume of tissue given that all the available N₂ at P2 has transformed from the dissolved state to the evolved state [71, 200]:

$$Decompression\;Dose = \left(\frac{P_1N_2}{P_2}\right) - 0.79 \quad \text{(Equation 3)}$$

where decompression dose is 0 at sea level since [(11.6 / 14.7) – 0.79] is 0.

TR is an index of the true decompression dose and is fundamental to other formal expressions of decompression dose as evolved gas. Given an abundance of quality research data, the bottom of the S-shaped curve on a DCS versus TR dose-response curve would be nearly flat over a range of TR to, say, 1.1. The flat region is an indication that decompression dose must exceed some critical value. TR is utilitarian, easy to use in statistical regression models to describe DCS and VGE outcomes from combined research trials over a range of TRs. TR, or R-value in NASA terminology, becomes a number that cannot be exceeded. For example, an R-value of 1.65 or less is acceptable for EVA operations in the 4.3 psia EMU from the Shuttle, but this R-value of 1.65 in an EMU does not mean the P(DCS) is zero [42, 182].

Risk and reward must be balanced to achieve an operational protocol, and finding this balance is as much an art as a science. Operations using the Russian *Orlan* spacesuit at 5.8 psia result in an R-value of about 1.85 to provide a P(DCS) that is the equivalent of the P(DCS) in the EMU, so the acceptable R-value (TR) is not an absolute, but in this case is a function of the suit pressure [201, 202]. The DCS research and operational EVA experience in the Russian space program is too extensive to summarize here [203] and parallels the efforts in the U.S. space program.

## Statistical and Biophysical Models

The integration of biophysical models of tissue bubble dynamics with statistical models of DCS and VGE outcomes from hypobaric exposures using logistic regression or survival analysis has led to significant advances in the development of probabilistic risk models in the last 20 years. For example, estimating a DCS risk model requires data that contains (1) the dichotomous DCS outcome (presence or absence) for multiple test results obtained over various experimental conditions, (2) explanatory variables such as decompression dose, which categorize or describe the experimental conditions and (3) demographic information pertaining to the test subjects. With this data, once can then estimate a risk model with logistic regression where the probability of DCS is expressed as logistic function or Hill equation with dose as input.

Simple descriptions of decompression dose such as TR or ΔP approximate the true dose [6, 76] whereas models about tissue bubble dynamics strive to define the true dose through diffusion-based physics and consideration of mass-balance [204-206] and more recently [198, 207-210]. Those referenced, and many others, too, contribute to a single evolving model to describe the P(DCS) in both diving and altitude depressurizations by invoking multiple tissue compartments, multiple finitely diffusible gases, and a distribution of bubble nuclei that begin to grow at
---
different times during depressurization. Others have concentrated just on hypobaric depressurizations [110, 176, 182, 201, 211-213]. Recent advances in probabilistic modeling came through the use of techniques from survival analysis Additional details about probabilistic DCS modeling are available [8, 214].

## *Tissue Bubble Dynamics Model (TBDM)*

The TBDM is a biophysical model of bubble growth in tissue [206] that has been used in development of decompression protocols for more than 25,000 commercial dives and used by NASA in the development of EVA prebreathe protocols [215]. In the model, assumed fixed values for several parameters, such as blood-tissue N₂ partition coefficient, initial radius of micronuclei, N₂ diffusivity between tissue and bubble, surface tension on a spherical bubble, and tissue bulk modulus are used to describe mass balance of tissue and bubble gases for a single growing bubble in a unit volume of tissue (details in Figure 8).

When inputted with the relevant durations, rates, pressures, and gas compositions the TBDM generates an output called bubble growth index (BGI), which is the time-varying ratio of bubble radius to an initial 3-μm radius of the bubble nucleus. The BGI for a decompression exposure is calculated over the duration of the exposure with the peak BGI value typically being used as the primary measure of decompression stress. Although the TBDM accommodates modeling of multiple half-time compartments to reflect the varying rates at which different body tissues take up and eliminate inert gases, the model typically includes only a 360-minute theoretical half-time for tissue N₂ kinetics when it is used to estimate decompression stress during EVAs.
---
$$\frac{dr}{dt} = \frac{-\alpha D}{h}\left(P_B-vt+\frac{2\gamma}{r}+\frac{4}{3}\pi r^3M-P_i-P_{met}\right)+\frac{r\nu}{3}$$

$$P_B-vt+\frac{4\gamma}{3r}+\frac{8}{3}\pi r^3M$$

**r** = bubble radius (cm)
**t** = time (sec)
**α** = Ostwald N₂ solubility
(0.0125 cm³ₑₐₛ/cm³ₜᵢₛₛᵤₑ for water at 37°C)
**D** = diffusion coefficient (2.0×10⁻⁵cm²/sec for water
**h** = bubble film thickness (3.0×10⁻⁴ cm)
**P₍ₕ₎** = initial ambient pressure (dyne/cm²)
**v** = ascent or descent rate (dyne/cm²×t)
**g** = surface tension (30 dyne/cm)
**M** = tissue modulus of elasticity, the ratio of bulk modulus (H) of 2.5×10⁸ dyne/cm² to articular cartilage
volume (H/cm³ₜᵢₛₛᵤₑ = M, dyne/cm²×cm³) times bubble volume ⁴⁄₃πr³ to compute a deformation
pressure (dyne/cm²)
**Pᵢ** = total tissue tension of all inert gases (dyne/cm²) in the general model but is specifically tissue N₂
tension (PₜᵢₛN₂) in EVA applications
**Pₘₑₜ** = metabolic gas (O₂+CO₂+H₂O) tensions (1.76×10⁵ dyne/cm², or 132 mmHg)

**Figure 8 Tissue Bubble Dynamic Model equation and parameters**

A statistical analysis of 6437 laboratory dives (430 DCS cases) compared predictions of the TBDM to the Workman M-value and the Hempleman PrT index, with TBDM predictions (BGI) yielding best log-Likelihood and Hosmer-Lemeshow (H-L) goodness-of-fit test [206]. BGI also provided significant prediction (p < 0.01) and goodness-of-fit for DCS (H-L p=.35) and VGE (H-L p=.55) data in 345 altitude decompression exposures (57 DCS cases, 16.5% DCS, 41.4% VGE) including prebreathe staged decompressions, all with exercise at altitude and including data points at 10.2, 6.0, and 4.3 psia [163, 164].

## Modeling and Operations

One reasonable expectation from modeling is that fewer trials, or even no trials, are performed before accepting a variation of a tested protocol if the model computes an acceptable P(DCS), P(serious DCS), or even P(Grade IV VGE). Such was the case in a recent decision to accept the campout PB for ISS without direct testing of this variant of the Shuttle 10.2 psia staged PB [215]. Aside from increasing computational efficiency for complex models, probabilistic modeling will significantly advance when the link is quantified between evolved gas in tissue and the perception of pain by the central nervous system [71]. An assumption in modeling is that the outcome variable is known with certainty, which is not the case [6, 45, 216], and adds an additional level of uncertainty to probabilistic modeling. Table 6 shows the DCS incidence from PB protocol ground validation trials in comparison to the flight DCS incidence and the modeling predictions that consider the operational changes from the ground trial protocol to the in-flight operational PB protocol [67]. Accepting a new PB protocol without prior ground testing validation is rare, but
---
the ISS campout protocol was accepted in 2005 based on empirical evidence and modeling analysis. It has been successfully used from ISS to support over 145 person EVAs to date.

Table 6: Observed and model-estimated probability of DCS for NASA prebreathe protocols as of November 2, 2022

| Prebreathe Protocol | Ground Subjects Tested | Ground Trial DCS Incidence (95% CL\*) | Model Prediction P(DCS) (95% CI\*\*) | EVAs using PB Option | Flight DCS Incidence (95% CL\*) |
| ------------------- | ---------------------- | ------------------------------------- | ------------------------------------ | -------------------- | ------------------------------- |
| 4-hr In-Suit        | 28                     | 21.40% (9.8-38.0%)                    | 4.60% (2.2-9.4%)                     | 6                    | 0% (0.0-60.0%)                  |
| Campout             | --                     | --                                    | 2.80% (1.2-5.9%)                     | 146                  | 0% (0.0-2.7%)                   |
| CEVIS               | 45                     | 0% (0.0-6.5%)                         | 2.00% (0.4-9.2%)                     | 52                   | 0% (0.0-9.2%)                   |
| ISLE                | 47                     | 4.20% (0.7-12.8%)                     | 0.30% (0.01-6.3%††)                  | 130                  | 0% No 95% CL calculated         |

*From binomial distribution – one-side 95% CL
**From regression models that provides 95% CI
†Model predictions include operational prebreathe margin and effects of microgravity.
††Based on option 1 operational prebreathe given nominal 6.8 ml/kg/min.

Existing models can only be extrapolated to the Exploration Atmosphere environment because the data underlying the model assumptions are based on depressurizations from 14.7 psia. An example of the application of probabilistic DCS models is provided in Table 7. The simulations for final in-suit PB times are based on an assumption of equilibrating to an atmosphere of 8.0 psia with 32% O₂ prior to the final in-suit PB. Even with the recent recommendation to adjust to 8.2 psia with 34% O₂, the partial pressure of N₂ remains the same, therefore the computed P(DCS) would not change [217].
---
# Table 7: Examples of model-estimated P(DCS) for Simulated Lunar Mission

| PIN₂       | PB (min) | TR   | P(DCS) (95% CI)    | P(VGE)             | P(GIV VGE) | P(serious DCS) |
| ---------- | -------- | ---- | ------------------ | ------------------ | ---------- | -------------- |
| 5.57       | 0        | 1.29 | 0.13 (0-0.30)\*    | 0.20               | 0.19       | 0.003          |
| 5.57       | 22       | 1.25 | 0.099 (0-0.26)     | 0.15               | 0.16       | 0.002          |
| 5.44       | 0        | 1.26 | 0.10 (0-0.27)      | 0.17               | 0.17       | 0.003          |
| 5.44       | 22       | 1.22 | 0.082 (0-0.21)     | 0.13               | 0.14       | 0.002          |
| 5.44       | 30       | 1.19 | 0.06 (0-0.18)      | 0.10               | 0.12       | 0.0017         |
| References |          |      | Conkin et al. 1996 | Conkin et al. 1990 | #          | Conkin 2001    |

* All estimates are extrapolations from statistical models.
* Results based on 8-hr EVA with equivalent 1-G ambulation and mild exercise.
* EVA after equilibration to 8.0 psia with 32% O₂.
* # unpublished Grade IV VGE regression from Conkin, n = 549 NASA records.

Additional analysis to supplement Table 7 is now summarized. EVAs at remote locations must maximize limited resources such as O₂ and minimize DCS. The proposed exploration atmosphere PB protocol requires astronauts to live in a mildly hypoxic atmosphere (PIO₂ = 128 mmHg) at 8.2 psia with 34% O₂ while periodically performing EVAs at 4.3 psia [164], 2015). Empirical data are required to confirm that the protocol meets the current accept requirements: ≤ 15% incidence of Type I DCS, ≤ 20% incidence of Grade IV VGE, both at 95% statistical confidence, with no Type II DCS symptom during the validation trial. A recent DCS survival model [218, 219] calculates a low probability of DCS of 1.5% (0.8 to 2.8%, 95% CL) for a 6-hr simulated EVA for physically active ambulatory subjects based on a computed tissue ratio of 1.22, a bubble growth index of 17, a body mass index of 24, and age of 32 yr, and increases to 2.3% (1.2% to 4.4%) for age 45.

## Expert Opinion – Decompression Sickness

Despite the promising, albeit limited, track record of DCS during spaceflight, future exploration missions will be breaking new territory. In the ~2400hrs of human EVA experience, only 83 hours were on the surface of a planetary body, and all of those were done from a 100% O₂ cabin. Thus, the are no instances of surface EVAs with decompression. Based on the expected higher metabolic rates, increased use of lower extremities, and gravity affecting fluid shifts/distribution, a higher risk of DCS is expected during surface EVAs. Some studies had a component of ambulation (as opposed to strict bedrest), and this showed a higher risk of DCS [149]. Although some models account for this 'ambulation' as a Boolean variable in the models [220], there is yet no in-flight data to compare the models to.

51
---
## DCS Treatment Capability

While the primary approach to mitigating DCS is to avoid it in the first place, there is also a need to determine necessary treatment for DCS should it happen on the ground or in orbit. DCS treatment capability is mandated in NASA-STD-3001 Volume 2 Rev C as [V2 6009]: The system shall provide DCS treatment capability. For any DCS that occurs on the ground during research studies and during EVA training in the NBL and altitude chambers can use a combination of ground level oxygen and hyperbaric chamber for the treatment of any DCS cases. For DCS that occurs during spaceflight, the hyperbaric chamber option is not available, but the combination of suit and vehicle pressure can be used to provide mild hyperbaric therapy and by keeping the astronaut in the EVA suit, a high %O2 environment can be sustained as well.

Per the request of a standing research panel recommendation, DCS treatment capability on orbit was added as a gap to the DCS risk, resulting in a retrospective data mining study and publication of the DCS treatment model [218]. In addition to these studies, we have the treatment plan for DCS on the ISS and can demonstrate the theoretical resolution of a bubble using the Tissue Bubble Dynamics Model.

A major gap in knowledge regarding DCS treatment is the effectiveness of repressurization to a vehicle pressure that is less than 14.7 psia. Most Exploration vehicles intend to operate at vehicle pressures less than 14.7 psia, with vehicles in cis-lunar space operating at or around 10.2 psia and vehicles on the lunar surface operating at 8.2 psia. With vehicles planning to operate at these lower pressures, it is unknown if the capability of returning to 14.7 psia is required for adequate DCS treatment. This question was analyzed and resulted in several program specific requirements for vehicle atmospheres, specific suit pressures and adequate resources for DCS treatment. This analysis is best summarized in an abstract and presentation given at the Aerospace Medical Association in 2022 [221].

Ground level O2 is an effective treatment for hypobaric DCS in most cases [218]. In most of these cases, the exposure can be terminated promptly, but in the case of EVA on the ISS, there could be up to a 30-minute EVA terminate duration. In addition, the most effective way of providing high % O2 to the affected crewmember is to remain in the suit, therefore, DCS treatment on the ISS involves the stacked pressure of the habitat (14.7 psia) with the EMU suit (4.3 psid) for a total of 19.0 psia and the >95% O2 in the suit. If symptoms do not resolve, additional pressure can be provided by attaching the Bend Treatment Apparatus (BTA) over the positive pressure relief valve and a suit pressure of 6.0 or 8.0 psid can be achieved. Pressurization of the EMU to 8.0 psid would also lead to a requirement to recertify the suit. The DCS treatment model [218] predicts 91-97.5% probability of symptom resolution [P(SR)] with the stacked vehicle and suit pressure of 19.0 psia [221]. P(SR) increase to 94-98.5% symptom resolution when adding the BTA and taking suit pressure up to 8.0 psid for a total of 22.7 psia. In addition, the duration from DCS symptom recognition to full bubble resolution was modeled to take 2 hr 55 min assuming full use of the BTA based on the TBDM.
---
In exploration scenarios with cabin pressures as low as 8.2 psia, there was a need to determine if the cabin needed to be able to achieve a higher pressure for DCS treatment. Unlike the EMU, the exploration EVA suits will likely be capable of repressurizing to 8.2 psia during an EVA. When humans are in equilibrium with the 8.2 psia cabin pressure, the immediate repress to 8.2 psia during the EVA effectively halts bubble growth and stabilizes the DCS progression, although the P(SR) only ranges from 48-67% indicating that it may not be sufficient pressure to immediately resolve symptoms. Therefore, it is still likely that a DCS event would lead to EVA termination. Using the longest possible EVA termination duration of 1 hour, the time from DCS symptom recognition to full bubble resolution was estimated to take 3 hr 49 min. Using the ISS case as a reference, this is less than 1 hour difference and likely a very similar result if the BTA was not used. Therefore, when the EVA suit is capable of pressurizing to 8.2 psia during an EVA, the habitat pressure of 8.2 (or 10.2) psia is likely sufficient to treat DCS effectively when combined with the additional pressure and high O2% of the exploration EVA suit.
---
## SECTION II: Hypoxia

### Risk Statement:
Given that future human exploration missions require robust, flexible Extravehicular Activity (EVA) architecture protocols that include the use of a reduced pressure cabin atmosphere enabling staged denitrogenation, there is a possibility that this atmosphere could result in compromised health and performance to the crewmember due to exposure to mild hypobaric hypoxia.

> Note: Although severe hypoxia is a risk during spaceflight due to a failure in pressure control or oxygen regulation, the focus of this risk and this evidence report will be on the risk of mild hypoxia associated with staged dinitrogenation as described in the DCS section above. Standards, requirements, and hazard controls for severe hypoxia are covered elsewhere in the program.

### Introduction: Hypoxia
One could eliminate the risk of DCS – and the associated onerous PB procedures – by transitioning to a pure oxygen atmosphere and slowly decreasing the environmental pressure as low as necessary to match the suit pressure. Although this solution was used early in the space program through the Apollo landings, high fractions of oxygen carry an increased risk of fire hazard. While adding nitrogen back into the atmosphere to keep the oxygen fraction under 40% dramatically decreases the risk of fire, the total pressure must increase, otherwise the partial pressure of oxygen (fraction of oxygen * total atmospheric pressure) will decrease below physiologic limits. While both pressure and fraction of oxygen can be kept somewhat below sea-level equivalents, it comes at the cost of hypoxic stress to the crew. Levels of hypoxia comparable to high altitude regions of Earth, however, may be considered.

Although certain mountainous regions of Earth reach physiologically intolerable altitudes, some cities – and even whole civilizations - have managed to flourish close these limits. Only in the last ~200 years has a systematic scientific investigation of the effects of altitude and reduced oxygen levels been studied. Similar to early studies of DCS (indeed, many of the early scientists studied hypoxia and DCS simultaneously), the ability to scientifically investigate the physiological effects depended on the development of technologies such as vacuum pumps, airtight chambers, and of course the invention of the hot air (and later gas) balloons, which allowed scientist-aeronauts to rapidly ascend animals (or humans) rapidly to high altitudes. A pertinent example of this are the flights by Glashier and Coxwell, who attained altitudes as high as 35'000ft in 1862 but were both unconscious due to hypoxia. A similar, but ill-fated flight in 1875 by Tissandier, Spinelli and Sivel resulted in the death of the latter two due to hypoxia. During the selection of parameters for the Exploration Atmosphere, a small amount of hypoxic stress was permitted so that while the pressure altitude is equivalent to ~16'000ft (4800m), the increase in fraction of oxygen lowers it to an equivalent altitude of approximately 4000ft (1200m) – 128mmHg PIO₂ – and is

54
---
## Human Spaceflight Evidence – Hypoxia

NASA's initial capsule designs (Mercury, Gemini), which minimized structural pressure differentials and were ultimately focused for Lunar EVAs (Apollo), used 100% O2 atmospheres. Thus, despite overall low atmospheric pressures (~5psi, 34.5kPa), these cabins were physiologically normoxic (PIO₂ > 150mmHg, Table 8) and could technically be considered hyperoxic (PIO₂ = 212 mmHg).

With the advent of the Space Shuttle program and plans for a future research space station, spacecraft atmospheres were matched to sea level conditions as this would enhance scientific studies using ground controls and significantly decrease fire risk. As described in the DCS sections above, however, this resulted in extremely onerous EVA preparations. During the Shuttle program, a compromise was reached by increasing the cabin FIO2 to the maximum allowable limit – 26.5% - and concomitantly decreasing the cabin pressure not just to maintain, but actually depress the partial pressure of oxygen from the sea-level 149 mmHg to 127 mmHg, comparable to a ~4000ft (1200m) altitude exposure, as detailed in the "Shuttle Campout" prebreathe protocol detailed above. This level of hypoxia was well tolerated during 41 Shuttle flights which used this protocol to expedite EVA preparations. The average duration at reduced pressure was 3.21 ± 2.18 days and was used for up to 8.1 consecutive days during STS-61 [222]. A retrospective study evaluated medical questionnaires and postflight medical debriefs and showed that the likelihood of reporting a symptom that could possibly be attributed to hypoxic exposure did not increase as compared to missions that remained at 14.7 psia for the whole duration [222]. Another interesting and relevant study was performed during the Shuttle program from 1995-1996. This study was evaluated potential changes in hemoglobin O2 saturation (SPO2) when comparing equivalent levels of hypoxic stress (PIO₂ = 127 mmHg) preflight, inflight, and postflight (R+0 and R+2). Results showed no difference is SPO2 during the inflight measurement indicating that that microgravity did not alter the body's ability to compensate for mild hypoxia [223].

The Shuttle staged protocol was adapted by ISS operations by isolating the airlock from the rest of the modules and depressurizing it to 10.2psi/26.5% for the crew to sleep in (the requirement was a minimum of 8hrs, 40min). However, due to the lack of amenities in the airlock and a significant logistical overhead (unrelated to any physiologic impacts of the atmosphere), it was replaced with other prebreathe protocols. Despite its lack of recent usage, human spaceflight experience has failed to show any significant impacts associated with that level of hypoxia for short durations. The primary concern related to hypoxic exposure is often how the body adapts to the initial hypoxic exposure. Terrestrial altitude exposures at a PIO₂ of 127 mmHg are well tolerated by most people, although some decrement in maximum performance can be seen during intense exercise. Therefore, the duration of acceptable exposure at a mildly hypoxic environment of PIO₂ = 127 mmHg was extended from 7 days based on past Shuttle program experience to "indefinite with monitoring" in the NASA Standard:
---
> "There is no indication on Earth that living and working with chronic PIO2 of 127 mmHg degrades health or performance. There are no indications or predictions based on limited past experience that extending exposure time with PIO2 of 127 mmHg in micro or partial gravity past 7 days leads to degradation of health or performance in otherwise healthy astronauts. There is no opportunity to collect data in microgravity with PIO2 of 127 mmHg to cover the durations of Exploration Class missions, so a health monitoring and mitigation plan are required to implement this condition. These guiding PIO2 values may change as further research yields information to better define the physiological limits and acceptable duration for an alternative space flight system environment" (NASA-STD-3001 Vol-2 Rev C).

## Table 8: Comparison of Cabin and Suit Atmospheres

| Environment                           | Pressurepsi (kPa) | O2Percent | ppO2(mmHg) | PIO2(mmHg) | EAA ft (m)  | ppN2(mmHg) |
| ------------------------------------- | ----------------- | --------- | ---------- | ---------- | ----------- | ---------- |
| Sea Level                             | 14.7 (101.3)      | 21        | 160        | 150        | 0 (0)       | 600        |
| Mercury                               | 5 (34.5)          | 100       | 259        | 212        | (hyperoxic) | 0          |
| Gemini                                | 5 (34.5)          | 100       | 259        | 212        | (hyperoxic) | 0          |
| Apollo                                | 5 (34.5)          | 100       | 259        | 212        | (hyperoxic) | 0          |
| Apollo A7L/B                          | 3.75 (25.8)       | 100       | 194        | 174        | (hyperoxic) | 0          |
| Skylab                                | 5 (34.5)          | 70        | 181        | 148        | 0 (0)       | 78         |
| Salyut/Mir                            | 14.7 (101.3)      | 21        | 160        | 150        | 0 (0)       | 600        |
| Shuttle                               | 14.7 (101.3)      | 21        | 160        | 150        | 0 (0)       | 600        |
| Shuttle – Staged                      | 10.2 (70.4)       | 26.5      | 140        | 127        | 4150 (1265) | 388        |
| EMU (Shuttle/ISS)                     | 4.3 (29.7)        | 100       | 222        | 175        | (hyperoxic) | 0          |
| ISS                                   | 14.7 (101.3)      | 21        | 160        | 150        | 0 (0)       | 600        |
| ISS Airlock Campout                   | 10.2 (70.4)       | 26.5      | 140        | 127        | 4150 (1265) | 388        |
| Exploration Atmosphere<br/>(Proposed) | 8.2 (56.6)        | 34        | 144        | 128        | 3980 (1213) | 280        |
| xEMU – lower limit<br/>(Proposed)     | 4.3 (29.7)        | 100       | 222        | 175        | (hyperoxic) | 0          |
| xEMU – upper limit<br/>(Proposed)     | 8.2 (56.6)        | 100       | 424        | 377        | (hyperoxic) | 0          |

*EAA = equivalent air altitude*

## Human Terrestrial Evidence - Hypoxia

Extensive human research as well as millennia of exposures has provided a wealth of physiological effects of altitude hypoxia. Millions of people are born, live and work above the
---
4000ft altitude (similar to the proposed Exploration Atmosphere) without ill effects. Indeed, Bhutan, Nepal and Tajikistan's average elevations are all above 10'000ft; La Paz, Bolivia has over 2 million inhabitants at 12'000ft (3640m) while over 20 million live in Mexico City at 7300ft (2240m). All these exposures imply long-term physiologic adaptation to the environment, a process that starts as soon as the exposure begins by changing respiratory and bicarbonate physiological set points. This adaptation takes a few days and completes in under 2 weeks. The first 2-3 days of adaptation can provoke symptoms and are often categorized as Acute Mountain Sickness (AMS). Note that because this is specifically for terrestrial exposures, the atmospheric composition is at a constant 21% O2 – only the overall pressure decreases with altitude, which causes a decrease in total pressure and thus a drop in the partial pressure of oxygen. Increasing the fraction of oxygen to increase the partial pressure of oxygen dissociates hypoxia from hypobaria; however, this can only occur in environments where the atmosphere is controlled (aircraft, altitude chambers, spacecraft). Thus, caution must be exercised when comparing altitude data (hypobaric hypoxia (HH)) to altered engineered environments (hypobaric normoxia (HN), normobaric hypoxia (NH), etc).

AMS affects individuals that ascend rapidly to altitude, with symptoms such as headache, nausea, vomiting, disturbed sleep, and poor physical performance[224]. The acute change in PI$$O_2$$ from normoxic 149 mmHg to the PI$$O_2$$ of 128 mmHg associated with the 8.2/34 Exploration Atmosphere environment can result in the possibility that some crewmembers may develop transient symptoms of AMS. Between 7% and 25% of adults may experience mild AMS near 2,000 m (6,562 ft, PI$$O_2$$ = 128 mmHg) [225, 226]. The risk of AMS is modified by several factors including the ascent rate to altitude, activity level at altitude, and individual susceptibility [227]. Hypobaric hypoxia appears to induce AMS to a greater extent than does either normobaric hypoxia or normoxic hypobaria [228].

AMS symptoms have been recorded using the Lake Louise Scoring System (LLSS, Figure 9) and include headache plus nausea, dizziness, fatigue, or sleeplessness that develops over a period of 6 to 24 hours. While expected to be mild and transient, these symptoms could potentially impact crew health and performance on critical mission tasks during lunar surface missions. AMS headaches are reported to be throbbing, bi-temporal or occipital, typically worse during the night and on awakening which can have implications for sleep quality. When combined with nausea, it can be likened to the flu or a hangover. Clinical findings confirm a change in mental status, ataxia, peripheral edema, or changes in performance (reduction in normal activities) [224].
---
| Symptoms                    | Severity                                  | Points |
| --------------------------- | ----------------------------------------- | ------ |
| Headache                    | No headache                               | 0      |
|                             | Mild headache                             | 1      |
|                             | Moderate headache                         | 2      |
|                             | Severe headache Incapacitating            | 3      |
| Gastrointestinal symptoms   | No gastrointestinal symptoms              | 0      |
|                             | Poor appetite or nausea                   | 1      |
|                             | Moderate nausea or vomiting               | 2      |
|                             | Severe nausea or vomiting, incapacitating | 3      |
| Fatigue and / or weakness   | Not tired or weak                         | 0      |
|                             | Mild fatigue/weakness                     | 1      |
|                             | Moderate fatigue/weakness                 | 2      |
|                             | Severe fatigue/weakness, incapacitating   | 3      |
| Dizziness / lightheadedness | Not dizzy                                 | 0      |
|                             | Mild dizziness                            | 1      |
|                             | Moderate dizziness                        | 2      |
|                             | Severe dizziness, incapacitating          | 3      |
| Difficulty of sleeping      | Slept as well as usual                    | 0      |
|                             | Did not sleep as well as usual            | 1      |
|                             | Woke up many times, poor night's sleep    | 2      |
|                             | Unable to sleep                           | 3      |

*Figure 9: Lake Louise Symptom Scoring System for AMS Diagnosis*

One of the largest studies on AMS was conducted by Anderson, et al. [229] during rapid ascent to Amundsen-Scott South Pole Station (2,835 m [9,300 ft]) in Antarctica. Of 246 subjects, 52% developed LLSS defined AMS (Figure 10). The most common symptoms were shortness of breath with activity (87%), sleeping difficulty (74%), headache (66%), fatigue (65%), and dizziness/lightheadedness (46%) (Figure 11). Symptom reports at the South Pole were mild to moderate in severity with symptom prevalence peaking on the day after arrival at altitude (day 2, approximately 12 to 18 hours after arrival); yet in greater than 20%, shortness of breath with activity, fatigue and sleep problems persisted through day 7. This reflected conventional knowledge that symptoms generally appear between 6 to 48 hours after arrival and resolve within the first 3 days [229].

Located on the high plateau of Antarctica at an elevation of 2,835 m (9,300 ft, PIO₂ ~ 105 mmHg), the environment of South Pole Station closely reflects the 8.2/34 environment as well as the operational profile of NASA mission scenarios. Most jobs at South Pole Station require physical activity, with a significant portion of personnel working outdoors. Activities include construction, heavy equipment operation, transport of supplies, science support, research, and fuel delivery [229]. This environment could serve as a high-fidelity, ground-based analog to research hypoxic effects within a spaceflight mission-like environment.
---
## Severity of altitude related symptoms during first week after rapid ascent to the south pole (2835m)

| Time first reached maximum symptom score | Percentage of participants |
| ---------------------------------------- | -------------------------- |
| Plane                                    | 5%                         |
| Day 1                                    | 28%                        |
| Day 2                                    | 31%                        |
| Day 3                                    | 10%                        |
| Day 4                                    | 5%                         |
| Day 5                                    | 2%                         |
| Day 6                                    | 2%                         |
| Day 7                                    | 2%                         |

Figure 10: Percentage participants that reached their maximum LLSS (AMS symptoms score) during the first 7 days at South Pole Station (2,835 m [9,300 ft])
---
## Severity of altitude related symptoms during first week after rapid ascent to the south pole (2835m)

|                                                                                                                                                                                             |                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| **Severity of headache**                                                                                                                                                                    | **Severity of fatigue** |
| Time	Severe	Moderate	Mild&#xA;Plane	0%	0%	15%&#xA;Day 1	0%	10%	40%&#xA;Day 2	0%	10%	35%&#xA;Day 3	0%	5%	15%&#xA;Day 4	0%	0%	15%&#xA;Day 5	0%	0%	15%&#xA;Day 6	0%	0%	10%&#xA;Day 7	0%	0%	10% |                         |

| Time  | Severe | Moderate | Mild |
| ----- | ------ | -------- | ---- |
| Plane | 0%     | 0%       | 15%  |
| Day 1 | 0%     | 5%       | 45%  |
| Day 2 | 0%     | 5%       | 40%  |
| Day 3 | 0%     | 5%       | 35%  |
| Day 4 | 0%     | 5%       | 25%  |
| Day 5 | 0%     | 5%       | 20%  |
| Day 6 | 0%     | 0%       | 15%  |
| Day 7 | 0%     | 0%       | 15%  |

Severity of difficulty sleeping
Severity of shortness of breath with activity

| Time  | Severe | Moderate | Mild |
| ----- | ------ | -------- | ---- |
| Plane | 0%     | 5%       | 10%  |
| Day 1 | 0%     | 5%       | 20%  |
| Day 2 | 5%     | 25%      | 25%  |
| Day 3 | 5%     | 10%      | 25%  |
| Day 4 | 0%     | 5%       | 25%  |
| Day 5 | 0%     | 5%       | 15%  |
| Day 6 | 0%     | 5%       | 20%  |
| Day 7 | 0%     | 5%       | 15%  |

| Time  | Severe | Moderate | Mild |
| ----- | ------ | -------- | ---- |
| Plane | 0%     | 0%       | 15%  |
| Day 1 | 5%     | 10%      | 55%  |
| Day 2 | 5%     | 10%      | 55%  |
| Day 3 | 5%     | 10%      | 55%  |
| Day 4 | 5%     | 5%       | 55%  |
| Day 5 | 0%     | 10%      | 50%  |
| Day 6 | 0%     | 5%       | 45%  |
| Day 7 | 0%     | 0%       | 45%  |

Survey Data —Timing

Figure 11: Severity of most commonly reported symptoms over the first week of exposure in personnel rapidly transported to the South Pole Station (2,835 m [9,300 ft])

### Modeling Evidence - Hypoxia

As altitude increases, pressure decreases non-linearly, and is affected by weather systems, temperature, and other factors. Physiological convention relies on the Equivalent Air Altitude (EAA) model – where PIO₂ is used as a physiological equivalence parameter – to compare atmospheres where the fraction of oxygen is different from 21%. This is done by using a standard atmospheric model (e.g., as defined in the International Standard Atmosphere, ISA-1976) to map a pressure to a specific altitude. The fraction of oxygen in the atmosphere is a constant 21% at all altitudes; per Dalton's Law, the partial pressure of oxygen, ppO₂ = Pambient * 0.21. However, because standard models assume dry environments, and the inspired air is saturated with water vapor in the upper airway, the water vapor is subtracted from the inhaled air. Water vapor pressure (PH2O) is determined by temperature, and assuming a constant core body temperature
---
of 37° C (97.6° F), this results in 47 mmHg. As a result, 'inspired' oxygen pressure, PiO₂ = (Pambient – PH₂O) * 0.21.

$$P_iO_2 = (P_{amb} - 47) * F_iO_2$$

Thus, any atmosphere with an oxygen fraction different than 21% can be mapped to a different altitude with 21% O₂ that would have the equivalent PiO₂; the "equivalent air altitude", EAA. This approach is easy to calculate and has proven effective over decades of research.

The EAA model is not, however, completely effective in translating across large pressure differentials. Although the hypoxic effects seem to match PiO₂, other symptoms associated with low atmospheric pressures, such as AMS, appear to have a component associated with absolute pressure independent of PiO₂ (Conkin, 2008). Human chamber studies at various fractions of oxygen and overall pressures would be needed to further understand this hypobaric and enriched-oxygen hypoxic environment for future Exploration Atmospheres.

An example of how a different model could be developed to evaluating hypoxic dose in these engineered environments is the Isohypoxic model [230], which adds an empirically derived correction factor to offset the EAA, effectively yielding, for the same PiO₂, a higher equivalent altitude when the absolute pressure is lowered. Table 9 compares the EAA, Isohypoxic and a straight conversion of pressure to altitude without compensation for increased oxygen ("pressure altitude").

## Table 9 - Hypoxic Model Comparison Across Proposed NASA Atmospheres

| Pressure (psia) | %O₂  | PiO₂ (mmHg) | Equivalent Air Altitude (ft)\* | Isohypoxic Altitude (ft)\*\* | Pressure Altitude (ft)\*\*\* | Reference Use Case                             |
| --------------- | ---- | ----------- | ------------------------------ | ---------------------------- | ---------------------------- | ---------------------------------------------- |
| 8.2             | 34   | 128         | 4000                           | 8300                         | 15700                        | Exploration Atmosphere                         |
| 9.8             | 28   | 128         | 4000                           | 6600                         | 11200                        |                                                |
| 10.2            | 26.5 | 127         | 4150                           | 6300                         | 10100                        | Historical Shuttle Staged / Campout Atmosphere |

*Equivalent Air Altitude (EAA) – assumes equivalent PiO₂ leads to the same level of hypoxic stress
**Isohypoxic Altitude [230] – accounts for additional stress due to absolute pressure
***Pressure Altitude does not compensate for increased %O2 and is provided as reference only

In each case, we use the EAA model as the most likely estimate of hypoxic stress, the isohypoxic model as the worst case upper bound for estimating hypoxic stress and ignore the pressure altitude conversion. The isohypoxic model was only compared against AMS symptoms, but it does provide a very helpful worst-case boundary to ensure discussion amongst stakeholders is kept in check with respect to understanding the true hypoxic stress.

61
---
## Expert Opinion – Hypoxia

The need to optimize repetitive EVA activity and reduce the burden of the prebreathe component (specifically on crew time and consumables), led to an expert panel - the Exploration Atmosphere Working Group - to propose an 8psi/32% O₂ atmosphere in 2005 [231]. This atmosphere was developed for the Constellation program, and with the cancellation of the program, was never implemented or even ground tested.

In 2012, interested in efficient and repetitive EVAs resurfaced, and additional review of the Exploration Atmosphere was adjusted to 8.2psi/34% O₂ to decrease the hypoxic stress, raising the PIO₂ from 117mmHg to 128mmHg. This also brought the hypoxic stress to a physiologically similar staged decompression atmosphere of 10.2 psia / 26.5% O₂ (PIO₂ = 127 mmHg) used on 40 different shuttle missions for approximately one week each flight.

Reviews of the DCS and Hypoxia risks by formal review committees have consistently had the same consensus option about the risk associated with mildly hypoxic, reduced pressure atmospheres, which is that it is likely to be well tolerated and there are no expected consequences that would be mission limiting or lead to long term health consequences [217].

With the announcement of the Artemis program in 2017 and a focus on repetitive and efficient Lunar EVAs, using a suit able capable of achieving an internal pressure of 8.2psi (and thus directly couple to an 8.2psi habitat/airlock) led to a resurgence of interest in the Exploration Atmosphere. Expert opinion on the atmospheric parameters has not changed – instead the focus has been to encourage ground testing of the proposed Exploration Atmosphere, both to validate the prebreathe protocol but also to characterize the associated hypobaric and hypoxic stress.

### Hypoxia Treatment Capability

Although unexpected and likely unnecessary, it is important to note the hypoxia is not a risk without treatment options. In some cases, O₂ can be supplied by mask to help relieve any symptoms or to aid in differential diagnosis. This capability will likely be limited due the possibility of enriching the vehicle with too much O₂. Should a member or members of the crew experience symptoms that do not resolve and are mission impacting, the vehicle pressure and/or O₂% can also likely be raised.

Finally, if neither mask or vehicle O₂ changes are sufficient or possible, the crewmember can be isolated in the spacesuit with enriched O₂. This capability is ensured with EVA suits, which have closed loop life support separate from the vehicle; however, it is not ensured with some launch, entry, abort (LEA) suits as some LEA suits are now using open loop flow designs. If that is the only way the LEA suit operates, then the hypoxic treatment capability of that space suit is limited as well as the ability of that suit to protect against DCS during a cabin depressurization event.
---
# Hyperoxia

Although hyperoxia is not a significant risk during spaceflight – and is only seen in limited training contexts – a very limited discussion of hyperoxic environments is included.

Hyperoxia is defined as any environment with higher-than-normal oxygen levels. In the context of physiology, any PIO₂ greater than 150mmHg (the 21% O₂ at sea-level equivalent dose) is considered hyperoxic. A *significant* hyperoxic exposure is considered when PIO₂ > 356mmHg (the equivalent of breathing > 50% O₂ at sea level), as exposures below that level are not associated with significant physiological pathology (see below).

There is no physiological benefit to a spaceflight environment that exceeds a sea level pressure or a normoxic PIO₂, therefore space vehicles rarely even have the capability to create hyperoxic environments. Additionally, these environments are now avoided due to the fire risk associated with hyperoxic environments. Further, since no directly reported cases of DCS have occurred, no DCS treatment in space has ever occurred. Therefore, the only significant hyperoxic exposure (>0.5 ATM ppO₂) during spaceflight occurs during O₂ prebreathe both on mask and in the suit, however, these are short duration and have not caused any medical concern.

## *Central Nervous system (CNS) toxicity*

The underwater training environments leveraged by NASA – the initial Weightless Environment Training Facility (WETF) and current NBL – provide crewmembers with the opportunity to train in conditions as realistic as possible for actual EVAs. A recent study has shown that although exposure levels exceed NOAA guidelines, no oxygen toxicity events have occurred in over 10,000 dives [232].

## *Pulmonary Toxicity (Lorrain-Smith Effect)*

Prolonged exposures (>24hrs) to moderate levels of elevated oxygen (above 0.5 atmospheres equivalent, PIO₂ > 356mmHg) are noted to cause progressive dyspnea, cough, and reversible decreases in lung vital capacity. Although this effect can be noted in clinical settings with positive pressure ventilation, spaceflight-associated exposures (whether in flight or in training) do not result in sufficiently prolonged exposures at oxygen fractions that result in pulmonary toxicity.

## *Atelectasis*

Early spaceflight missions including Mercury, Gemini and Apollo all operated at hyperoxic environments, but these were below any thresholds for CNS or pulmonary hyperoxic concerns. With the extended durations planned for Skylab mission, an inert gas, N₂, was added back to the environment to avoid risk of atelectasis. Human spaceflight standards now require the inclusion of an inert gas in the atmosphere for any vehicle: See NASA-STD-3001 Volume 2 Rev C - [V2 6002] Cabin atmospheric composition shall contain at least 30% diluent gas (assuming balance oxygen).
---
# SECTION III: Risk in the Context of Exploration Operational Scenarios

## Definition of Acceptable Risk for Decompression Sickness

DCS is a known risk during EVA that requires mitigation. Elimination of all risk through a lengthy PB prior to EVA is both impractical and virtually impossible to demonstrate due to the probabilistic nature of DCS. An alternative approach to engineering out DCS as a risk is to define acceptable risk. This approach necessitates the development of a standard of acceptable DCS risk for which countermeasures can then be evaluated against. This critical step of defining the acceptable level of DCS risk began as the initial step of the Prebreathe Reduction Program in 1997 with participation from the NASA EVA community, United States Navy, United States Air Force, and academic research community.

Some of the major factors considered in this process included:

* DCS risk per EVA based on flight, ground, and modeled data
* On-orbit DCS treatment capability
* Disposition of an astronaut that reports DCS
* NASA EVA community awareness of DCS
* Availability of EVA crewmembers to successfully complete the assembly of the ISS

The final product of this effort was the NASA DCS Risk Definition and Contingency Plan [215, 233], which led to the development of the following:

* Acceptable DCS Risk for the development of ISS PB Protocols – All protocols had to demonstrate total DCS < 15 percent at 95% Confidence Limit (CL), < 20 percent Grade IV VGE at 95% CL, no Type II (Serious) DCS.
* EVA Cuff Checklist that attaches to the cuff of the arm during EVA, which specifies a sequence of actions in the event of symptoms. This Cuff Checklist was not DCS specific, but rather provided instructions in the case of symptoms such as pain or paresthesia irrespective of whether the symptoms were caused by DCS or suit related trauma.
* DCS Disposition Policy that mandated the reporting of DCS symptoms both on the ground (chamber or NBL operations) and described the process by which an astronaut or would be evaluated and returned to flight status (JPR 1800.3).

This level of acceptable DCS risk used for the PB reduction program was used in the validation of 3 additional PB protocols, which were used to successful assemble the ISS and are still used to perform ISS maintenance EVAs. By validating operational PB protocols against this acceptable risk level, NASA has successfully prevented both serious Type II DCS and Type I pain only DCS. This acceptable risk level was reviewed by several JSC Human Health and Performance Directorate Boards and the NASA Headquarters Chief Health and Medical Office and subsequently entrenched as a new human spaceflight standard in the EVA section of NASA-STD-3001 Volume 1. Although developed specifically with the ISS assembly in mind (and thus
---
assuming multiple crews, low Earth orbit with multiple contingency landing sites for medical care) has nonetheless become the minimum standard for which all future PB protocols will need to test against. The focus of this standard was to protect against long- and short-term human health consequences, but it does not define any guidelines for expected EVA efficiency, crew time or consumables.

The acceptable risk for DCS is defined in the NASA Space flight Human-System Standard Volume 2, Revision C. Section 6.2.2.4 Decompression Sickness (DCS) Risk Identification:

> [V2 6008] Each program shall define mission unique DCS mitigation strategies to achieve the level of acceptable risk of DCS as defined below within 95% statistical confidence:
>
> a. DCS ≤ 15% (includes Type I or isolated cutis marmorata).
> b. Grade IV venous gas emboli (VGE) ≤ 20%.
> c. Prevent Type II DCS.
>
> [Rationale: DCS risk limits have been defined to develop coordinated requirements for the habitat (e.g., vehicle, EVA suit) including total pressure, ppO2 and prebreathe before vehicle or suit depressurization, which are all variables in DCS risk.]

This DCS standard specifically applies to EVA only and defines the overall acceptable risk with respect to minimize effects on long term crew health by ensuring that Type II symptoms are minimized and that any pain only symptoms are likely to respond very well to available treatment capabilities. It should be noted that this standard does not ensure mission success and does not cover unplanned decompressions of a vehicle where the whole crew would be exposed to the hypobaric environment.

Even if a denitrogenation protocol ensures this standard is met, there are still possible mission impacting results from the termination of EVA. Each program, especially exploration missions with a heavy emphasis on EVA to ensure mission success, will need to determine the threshold for actual DCS risk that will ensure a high probability of mission success. An example of this type of analysis was from the construction of the ISS. A multi-disciplinary team defined operational success as a 95% probability that 2 of 3 crewmembers would be EVA ready for the completion of all ISS assembly EVAs. This analysis drove an upper bound acceptable limit of 19% DCS risk to accomplish necessary operations. Because this was greater than the 15% risk needed for health concerns, the health limit was used. But, with future exploration missions involving as many as 5 EVAs over a week, the operational risk will certainly drive a lower acceptable DCS risk than 15%, thus necessitating either more aggressive denitrogenation strategies or a more realistic evaluation of true mission success needs.

While this DCS standard established a minimum threshold for protecting crew from DCS during EVA, it does not describe acceptable risk for vehicle decompressions such as when the crew would transition from a normobaric atmosphere to the Exploration Atmosphere (8.2 psia, 34% O2, balance N2). The primary difference in this case is that the whole crew is exposed to DCS risk
---
at the same time. An additional metric to consider would be the acceptable risk for contingency EVA scenarios. Currently, all contingency scenarios are handled as isolated events, but a pre-determined level of acceptable risk for contingency EVA and a supporting higher risk, but lower overhead PB protocol should be considered.

## Decompression Sickness Risk in Context of Exploration Mission Operational Scenarios

As of November 2022, there have been no reported cases of DCS during Shuttle and ISS missions due to adherence to PB protocols rigorously developed and validated specific to Shuttle and ISS operational environments and EVA scenarios. Although DCS risk has been greatly reduced through these PB protocols, it is at the expense of significant crew time and consumable usage. With the relatively infrequent number of EVAs during ISS missions, these time and consumables hits are considered acceptable, but this need for significant crew time and consumables will not meet the needs of NASA's Exploration programs.

The architectures being developed by NASA for future exploration beyond low earth orbit differ from previous vehicles and EVA systems in terms of vehicle saturation pressures, breathing mixtures, EVA frequency, EVA durations, and pressure profiles, and will almost certainly differ in terms of the definition of acceptable DCS risk with mission success possibly demanding a lower acceptable risk than what is necessary to minimize long term health consequences. In-situ DCS treatment capabilities are known to be different, although predicted to be effective (Dervay, 2022). One study demonstrated how the use of suit ports, variable pressure EVA suits, intermittent recompressions, and possibly abbreviated purges with PB gas mixtures of less than 100% oxygen represent a paradigm shift in the approach to EVA with the potential of reducing EVA crew overhead and consumables usage by two orders of magnitude (Abercromby *et al.* 2015). More recently, strategies to complete necessary prebreathe concurrently with airlock depressurization combined with starting the EVA at pressures greater than the planned EVA suit pressure of 4.3 psia, have demonstrated that DCS risk can be reduced even further without impacting timeline and with likely well tolerated performance impacts during EVA. However, the role and impact of these variables on the overall probability of DCS and the likely impact to EVA performance is theoretical, without empirical data to support the theory. Finally, NASA has contracted out the development of spacesuits, lunar landers, and pressurized rovers with the desire to limit requirements and provide as much flexibility for vendor designs. While this makes an exciting competitive environment, the ability to mitigate DCS and maximize EVA capability runs the risk of disconnects between vendors due to different solicitation periods, design review timelines and NASA oversight personnel.

## Operational and Programmatic Risk of Not Implementing the Exploration Atmosphere

Current and future spacesuit functionality requires decompression to perform EVA. Without the use of a staged denitrogenation protocol, such as proposed with the 8.2 psi/34% O2 Exploration Atmosphere or a zero-PB EVA suit operating at higher pressures, denitrogenation protocols will
---
remain lengthy. Much research could be performed to reduce the length of existing ISS PB protocols. Understanding how a break in PB affects P(DCS) would be a critical step. Also, understanding the differences in VGE, N₂ washout and micronuclei generation in the space flight environment would be of great benefit. **In the end, an operational mitigation strategy that relies on long O₂ PB as the primary strategy will result in longer more complicated EVA preparation timelines, higher consumables use, and reduce the flexibility and capabilities of Exploration EVA.**

An example of the consumables savings available through use of the 8.2/34 Exploration Atmosphere is by reducing the suit purge time by 6 min per EVA, achieving 80% O₂ in the spacesuit rather than 95%. This modestly increases P(DCS) risk but the calculated savings of 0.48 lb of gas and 6 minutes per person per EVA corresponds to more than 31 hours of crew time and 1800 lb of gas and tankage under the Constellation lunar architecture (Abercromby *et al.* 2015).

Of available strategies to significantly reduce denitrogenation time while maintaining acceptable DCS risk, the Exploration Atmosphere strategy is more promising than either a high-pressure EVA suit or an enhanced version of current ISS PB protocols.

Timeline Impacts are very difficult to assess because so many factors can be moved around, but a simple analysis can demonstrate the impact of a long prebreathe/denitrogenation time on crew sleep time if trying to preserve the maximum EVA time of 8 hours. The use of a 30 min O2 prebreathe from the 8.2/34 environment allowed the crew to complete all necessary activities and have an hour of margin. Shifting to the 10.2/26.5 atmosphere would require approximately 3.5h PB, thus removing all margin from the timeline and shortening sleep from 8 to 6.5 hours. Finally, should a sea level atmosphere be used, the associated 7-hour O2 PB to get to equivalent DCS risk would reduce sleep time to 2.5 hours, which is not feasible (Figure 12).

|     |                                                                                                                              |          |                        |                         |                          |    |             |   |   |   |   |   |   |   |                       |                      |                               |       |   |   |   |   |   |   |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | -------- | ---------------------- | ----------------------- | ------------------------ | -- | ----------- | - | - | - | - | - | - | - | --------------------- | -------------------- | ----------------------------- | ----- | - | - | - | - | - | - |
| SAT | 0000 0100 0200 0300 0400 0500 0600 0700 0800 0900 1000 1100 1200 1300 1400 1500 1600 1700 1800 1900 2000 2100 2200 2300 2400 |          |                        |                         |                          |    |             |   |   |   |   |   |   |   |                       |                      |                               |       |   |   |   |   |   |   |
|     | SLEEP<br/>(8.0 HRS TOTAL)                                                                                                    |          |                        | Postsleep<br/>1.5 hrs   | EVA Prep<br/>(excl. PB)  | PB | EVA (8 HRS) |   |   |   |   |   |   |   | Post-EVA<br/>Overhead | MARGIN<br/>(60 Mins) | Presleep<br/>1.5 hrs          | SLEEP |   |   |   |   |   |   |
|     | SLEEP<br/>(6.0 HRS TOTAL)                                                                                                    |          | Postsleep<br/>1.5 hrs  | EVA Prep<br/>(excl. PB) | Prebreathe<br/>(3.5 HRS) |    | EVA (8 HRS) |   |   |   |   |   |   |   | Post-EVA<br/>Overhead | Presleep<br/>1.5 hrs | SLEEP                         |       |   |   |   |   |   |   |
|     | Postsleep<br/>1.5 hrs                                                                                                        | EVA Prep | Prebreathe<br/>(7 HRS) |                         |                          |    | EVA (8 HRS) |   |   |   |   |   |   |   | Post-EVA<br/>Overhead | Presleep<br/>1.5 hrs | SLEEP<br/>(2.5 HRS<br/>TOTAL) |       |   |   |   |   |   |   |

Assumptions
1. DPCs are for system status checks and any general Q&A for crew
2. PMCs are for pre/post EVA medical status checks
3. Sleep period = 8 hrs, immediately following Presleep activity (no sleep shifting for crew during surface ops)
4. Post/presleep include routine system/HAB cks, hygiene and meal
5. EVA Prep includes pre-EVA conference with MCC

Figure 12: Impact of cabin atmosphere and pressure and associated prebreathe duration on mission timeline. Top timeline represents 8.2 psi/34% O2 exploration atmosphere, middle timeline represents 10.2 psi/26.5% O2 atmosphere, and bottom timeline represents 14.7 psi/21% O2 atmosphere.

Further considerations for managing denitrogenation across multiple vehicles was discussed as part of the initial Lunar Human Landing System (HLS) solicitations. These vehicles were being designed with no O2 masks to facilitate PB and many LEA spacesuits operate open loop and cannot be used for O2 PB. Therefore, different scenarios were shown to potential providers to

67
---
demonstrate the rationale for selection of the 8.2psi/34% O₂ environment as the HLS reference. This table is shown in Figure 13.

|                                           | Scenario 1                                                                                                                                                                                                                                                                                                                                                                                                             | Scenario 2               | RecommendedScenario 3                                                   | Scenario 4             | Scenario 5                                 | AssumedConOps\*\*\*                                                                             |             |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ----------------------------------------------------------------------- | ---------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------- | ----------- |
| Gateway Atmosphere \*                     | 14.7, 21% O₂                                                                                                                                                                                                                                                                                                                                                                                                           | 10.2 psi, 26.5% O₂       | 10.2 psi, 26.5% O₂                                                      | 14.7 psi, 21% O₂       | 14.7 psi, 21% O₂                           | Orion transit to Gateway                                                                        | TBD days    |
| Lander \*\*\* Atmosphere                  | 10.2 psi, 26.5% O₂                                                                                                                                                                                                                                                                                                                                                                                                     | 10.2 psi, 26.5% O₂       | 8.2 psi, 34% O₂                                                         | 14.7 psi, 21% O₂       | 8.2 psi, 34% O₂                            | Orion docked to Gateway                                                                         | 5 days      |
| Prebreathe prior to and/or during descent | 1+ hours TBR<br/>(on mask, or in suit)                                                                                                                                                                                                                                                                                                                                                                                 | None required            | None required                                                           | None                   | 3+ hours TBR<br/>(on mask, or in suit)     | Lander undock, transit to lunar surface (12 hrs)<br/>Post landing safe-ing & reconfig (\~4 hrs) | Lunar Day 1 |
| Minimum time in Lander prior to EVA       | Longer prebreathe if EVA prior to 36 hours                                                                                                                                                                                                                                                                                                                                                                             | No constraint            | No constraint after 24 hours<br/>Small PB penalty if earlier than 24hrs | None                   | Longer prebreathe if EVA prior to 36 hours | Crew Sleep (8 hrs)<br/>EVA 1                                                                    | Lunar Day 2 |
|                                           |                                                                                                                                                                                                                                                                                                                                                                                                                        |                          |                                                                         |                        |                                            | EVA 2                                                                                           | Lunar Day 3 |
| Estimated O₂ prebreathe prior to EVA \*\* | Estimate 3-3.5 hours TBR                                                                                                                                                                                                                                                                                                                                                                                               | Estimate 3-3.5 hours TBR | Estimate 0-30 mins TBR                                                  | Estimate 6-9 hours TBR | Estimate 0-30 mins TBR                     | No EVA                                                                                          | Lunar Day 4 |
|                                           |                                                                                                                                                                                                                                                                                                                                                                                                                        |                          |                                                                         |                        |                                            | EVA 3                                                                                           | Lunar Day 5 |
|                                           | \* Assume 36+ hours at atmosphere prior to lander undocking; balance N2 in all atmospheres<br/>\*\* Estimated prebreathe times are approximations and not validated; assume 6 hour EVA @ 4.3 psia.<br/>\*\*\* Assumed ConOps requires use of a reduced pressure, O₂ enriched environment to provide staged denitrogenation. Scenario 4 is provided for reference, but would probably not facilitate the assumed ConOps |                          |                                                                         |                        |                                            | EVA 4                                                                                           | Lunar Day 6 |
|                                           |                                                                                                                                                                                                                                                                                                                                                                                                                        |                          |                                                                         |                        |                                            | Lander ascent, return to Gateway                                                                | Lunar Day 7 |

Figure 13: HLS Initial Prebreathe Table for Lunar and Planetary scenarios (Reprint of Draft Lunar Prebreathe Table (Section No. HLS-HMTA-0031) [234]

## Monitoring Strategies for Assessing Hypoxia Risk Inflight

Given that there is no analog on Earth that can mimic all relevant changes associated with spaceflight and associated levels of hypobaric hypoxia, definitive research to address the risk is unavailable; therefore, an inflight monitoring plan to assess hypoxia symptoms during flight is required. Recommendations for inflight monitoring include:

* ECLSS monitoring is expected for every vehicle and should be made available to assess hypoxic risk/effects
* Oxygen saturation (pulse oximetry with perfusion index for signal quality validation)
* Sleep (Actigraphy)
* Venous thrombosis/vascular status (ultrasound)
* Cognition
* Exercise performance
* Blood biomarkers (hematocrit, hemoglobin, RBC, etc.)
○ There are mixed perspectives about blood cell changes associated with microgravity exposure. Early studies relying primarily on astronaut pre-flight to post-flight changes did indicate possible anemia which would not help with
---
hypoxic adaptation, but more recently, Kunz, et al. [235], demonstrated that astronaut do not manifest anemia inflight.

## Severe Acute Hypoxia Concerns

### High Altitude Pulmonary Edema (HAPE) and High Altitude Cerebral Edema (HACE)

Both HAPE and HACE are life threatening concerns that require immediate treatment and are best avoided. Both conditions have been associated with the uncompensated pressure altitudes, but because of the increased FIO2 added to planned Exploration Atmospheres, the risk of HAPE and HACE is considered negligible. These tend to be low risk conditions even at much higher altitudes and are often associated with rapid ascent to altitude and heavy workload at altitude [236]. EAA model predictions of hypoxic stress are well below the threshold stimulus. If considering the isohypoxic model as a worst-case estimate of hypoxic stress, this predicts hypoxic stress at the edge of any known cases. Given a healthy astronaut population combined with controlled pressure changes, HAPE and HACE are not currently considered risks in the spaceflight context.

### Acute Mountain Sickness

Relevant literature [230] and statistical analysis of available data [226] suggest that the 4000-ft computed EAA for the 8.2/34 Exploration Atmosphere environment may have more risk of AMS than one would expect at this altitude. This independent pressure effect on true hypoxic dose has been suspected since 1946. Ever since the derivation of the alveolar gas equation was published [237] there has been a physiologic foundation to expect different outcomes under normobaric and hypobaric hypoxia given the same hypoxic PIO2, termed the nitrogen dilution or the respiratory exchange ratio effect [238]. Without considering acclimatization to mild hypoxia from one vehicle to the next, there is about a 18% chance of AMS per crewmember for the initial proposed 8.2/34 environment [226]; this also assumes no further negative interactions due to adaptation to microgravity. Predictions of AMS risk for direct transition from sea level to potential cabin atmospheres is shown in Table 10. However, risk can be reduced by controlled pressure changes. Also, it should be noted that there is no evidence of AMS symptoms from shuttle missions [222].
---
## Table 10. AMS Risk Calculations for Various Atmospheres

| Pressure (psia) | %O   | EAA (ft) | Isohypoxic Altitude (ft) | P(AMS) |
| --------------- | ---- | -------- | ------------------------ | ------ |
| 8.2             | 34   | 4000     | 8300                     | 17.5%  |
| 9.8             | 28   | 4000     | 6600                     | 9.8%   |
| 10.2            | 26.5 | 4150     | 6300                     | 10.5%  |

Further research is needed to measure the acute mild hypoxic response to the 8.2/34 environment. It seems that the magnitude of the pressure effect on true hypoxic dose is a function of the hypoxic PIO2. The pressure difference between 11.8 and 8.0 psia may or may not be sufficient to measure a pressure effect on the onset, intensity, and incidence of AMS, given a reasonable sample of human subjects. If time and money resources are not available, then staged decompression and pharmacologic mitigation strategies should be developed to reduce and manage the predicted risk of AMS.

## Transition to Exploration Atmosphere

Given crew will be launching from a sea-level atmosphere and eventually switch to a particular Exploration Atmosphere in preparation for extended EVA operations, a transition needs to occur at some stage. As discussed above, rapid transitions with large pressure drops result in higher risk of developing AMS. Thus, a gradual decompression over several days would be effective in avoiding AMS. Once stabilized at the new atmospheric parameters, the partial pressure of N2 in the body equilibrates. This, however, may also require several days: equilibrating the 360-min compartment used in much of the altitude DCS calculations could take 24-36 hrs (4-6 half times, or 94-98% equilibration), but most DCS models include slower compartments going up to 480min (TBDM) or 635min (Buhlmann model), as cases of DCS in commercial diving have shown these compartments play a role in ascents from saturation. Depending on mission profiles and timelines, as well as atmospheric control systems and tolerances of the different vehicles, an accelerated transition timeline may be necessary. Although decompression models can implicitly leverage use of oxygen (PB) to accelerate the elimination of N2 and thus transition to the new atmosphere, the only similar tool that exists in AMS is the use of carbonic anhydrase inhibitors. However, there is no "AMS model" that exists, and that could use pharmacologic intervention as a potential accelerator. Future research may shed light on the potential benefits of such interventions. In the meantime, minimizing critical tasks and controlling workload stress could help mitigate any transient hypoxic or AMS-related deficits elicited during the transition period before adaptation occurs.
---
## Hyperoxia

Excessive partial pressure of oxygen can also be detrimental, and although there are few situations in which crew may be exposed to high partial pressures of oxygen, treatment for DCS is one such situation. Although not extensively verified at various atmospheric pressures, a general principle is that if the partial pressure of oxygen is kept at less than 0.5 atmospheres, no oxygen toxicity will develop. Another situation where elevated partial pressure of oxygen is found is during underwater (neutral buoyancy) training. Partial pressures equivalent to 1 atmosphere are common during EMU training (operating at 4.0psi, ~28kPa), and with the push towards higher pressure suits, as referenced above, may result in much higher exposures. Careful exposure controls, medical monitoring and emergency planning has, so far, resulted in no incidents due to hyperoxia during training.
---
# SECTION IV: Directed Acyclic Graphs

## Decompression Sickness Directed Acyclic Graph

Figure 14 presents the current approved Directed Acyclic Graph (DAG) as managed by the NASA Human Systems Risk Board. Review of the current DAG and associated level of evidence assessment of each arrow (relationships) is supported by evidence presented in the report.

![Figure 14: DCS Risk DAG - A complex directed acyclic graph showing relationships between various factors affecting decompression sickness risk. The graph contains multiple colored nodes (orange, blue, black, and gray) connected by directional arrows. Key nodes include Hostile Closed Environment, Altered Gravity, Distance from Earth, DCS Type I, DCS Type II, and various operational factors. A small box in the lower left lists denitrogenation methods.]

Figure 14: DCS Risk DAG

The primary spaceflight hazard impacting DCS is the **Hostile Closed Environment** – with a closed environment, the chosen total pressure, in addition to O₂ and N₂ partial pressures, for the vehicle and space suit drive the DCS risk and treatment capability.

Secondary hazards include **Altered Gravity** – expected increases in EVA workload, weight-bearing tasks, and joint forces associated with planetary gravity EVA increase DCS risk as compared to microgravity EVA, and **Distance from Earth** – drives the vehicle design and provides limits to resources and consumables. Additionally, it can impact the ability to return a crewmember to the ground for definitive medical care.

DCS is represented by two nodes DCS Type I and Type II. **DCS Type I** is a mild environmental injury that primarily affects the joints, skin, and lymphatic vessels. **DCS Type II** is a severe, potentially life-threatening environmental injury that often affects vital organ systems, including the brain and spinal cord, respiratory system, and circulatory system. It is possible for DCS Type I to progress to DCS Type II.

In the spaceflight environment, four important factors contribute to DCS occurrence.
1. **Denitrogenation** is the reduction of nitrogen from blood and body tissues to minimize the formation of gas bubbles and mitigate DCS.
---
2. **Depressurization** can lead to DCS; therefore, it occurs after **Denitrogenation** to minimize DCS risk.

3. **EVA Operations** are directly affected by **Denitrogenation** (including O2 prebreathe time), which depends on **Atmospheric Conditions**. For example, Exploration Atmospheres are altered **Atmospheric Conditions** designed to decrease **Denitrogenation** time while keeping the risk of DCS acceptably low and minimizing the potential for **Loss of Mission Objectives**.

4. **Individual Factors** that may contribute to DCS are screened for during **Astronaut Selection**. An example is major cardiac abnormalities such as atrial/septal defects that could allow gas bubbles to pass from the heart's right to the left side. Previous decompression illness experiences are also discussed and dispositioned on an individual case basis.

Either type of DCS can impact **Individual Readiness**, **Crew Capability**, and **Task Performance** by introducing functional impairments that can lead to **Loss of EVA(s)**, **Loss of Mission Objectives**, or **Loss of Mission**. **DCS Type II**, **Arterial Gas Embolism**, and **Ebullism**, should they occur, can lead to **Loss of Crew Life** or permanent **Long Term Health Outcomes**. The ability to **Detect Long Term Health Outcomes** depends on ground-based **Surveillance** programs.

The likelihood of experiencing DCS is associated with physical exertion (i.e., metabolic rate and joint forces) captured here as **Workload**. This factor depends on **EVA Operations**, a category node that includes **EVA Frequency**, **EVA Duration**, **Planned EVA Content**, **EVA Task Timeline**, and **EVA Decision Support**. These components of **EVA Operations** are explicitly demonstrated in the EVA Risk DAG.

**Vehicle Design** determines:
* **Atmospheric Conditions** – The primary DCS concern is the partial pressure of N2.
* **Airlock Design** - The **Depressurization** and repressurization rates factor into barotrauma prevention, DCS risk, and treatment capability. The combination of **Suit Design**, prebreathe/**Denitrogenation** protocol, and **Airlock Design** may necessitate different **Depressurization** and repressurization cycles as well.
* **Crew Health and Performance System** determines the level of **Medical Diagnostic Capability** and **Medical Treatment Capability**. The **Medical Diagnostic Capability** is important to **Detect DCS** and distinguish between mild DCS symptoms and other injuries. It also includes specific training of the crewmember on DCS symptoms and treatment. **Medical Treatment Capability** depends in part on **Suit Design**. For example, the space suit, which is capable of over-pressurization, provides DCS treatment on the International Space Station (ISS).

The likelihood of **Vehicle** or **Suit Failure**, which can lead to **Depressurization**, is affected by **Vehicle Design**, **Suit Design**, and limitations of the **HSIA (Risk)**.
---
## DCS Integration with Other Risks:

The most obvious risks that are connected to the DCS risk include Hypoxia and EVA, because hypoxia is only nominally experienced by the crew due to operating in vehicle habitats to facilitate staged denitrogenation to reduce the time and resources to mitigate DCS prior to beginning EVA.

The other risk highly connected to DCS is the HSIA risk because DCS mitigation is best done through engineering solutions that must be included in the vehicle and suit design. Further, there can be multiple vehicles used to accomplish a whole mission and therefore the vehicle and suit design requirements need to work harmoniously across all vehicles used.

## Hypoxia Directed Acyclic Graph

This section will provide a review of the current DAG and Level of Evidence assessment of each arrow (relationships), as supported by evidence presented in the report.

![Figure 15: Hypoxia Risk DAG]

**Hostile Closed Environment** is the primary spaceflight hazard requiring NASA to create an engineered atmosphere optimized for mission success.

**Altered Gravity** leads towards negative physiologic changes in the body and so does hypoxia, therefore any nominal hypoxia must be driven by operational needs and minimized.

There are two levels of **Hypoxia** stemming from different sources that are concern in spaceflight. The **Hypoxia** node represents more severe hypoxia that can occur as a result of a **Suit Failure**, **Toxic Exposure**, or **Depressurization** from **Vehicle Failure**. This severity of hypoxia can lead to **Loss of Crew Life** or can impact **Individual Readiness** and **Crew Capability**.

74
---
**Mild Hypoxia** is a different concern that can lead to issues with **Cognitive Function**—which is affected by **Individual Factors**—Fatigue, Exercise Prescription, and **Medical (Risk)** conditions such as acute mountain sickness, and issues addressed by other Human System Risks including **DCS (Risk), Immune (Risk), SANS (Risk), Sleep (Risk), and Muscle/Aerobic (Risk)**.

**Atmospheric conditions** (specifically low pressure) can affect food processing (converting raw ingredients such as soybeans into tofu) or food preparation beyond simple heating and rehydration is conducted. This concern will be addressed by the Food and Nutrition Risk Team.

**Mild Hypoxia** is of concern when considering Exploration Atmospheres for example, where changes to **Atmospheric Conditions** during **Staged Denitrogenation** can expose astronauts to physiologic hypoxia that is at a low level and chronic over time. **Suit Failures** that are not catastrophic can also induce **Mild Hypoxia** and these can be caused by either **Suit Design** issues or **EVA Operations**. The level of hypoxia experienced is also dependent on the **Effective Exposure Duration**.

**Distance from Earth** affects the available mass, power, volume and bandwidth available to a **Crew Health and Performance System**. Issues addressed by the **HSIA (Risk)** contribute to **Vehicle Design** and capabilities of the **Crew Health and Performance System**, which enables **Environmental Monitoring Capability** that can **Detect Atmospheric Changes**. In cases where those changes warrant, countermeasures such as **Breathing Masks, Pressure Suits**, and **Compartment Isolation** can be implemented to protect **Individual Readiness, Crew Capability**, and health.

Historically pilots and astronauts are exposed to hypoxic conditions prior to flight so that they can understand how their unique symptoms are expressed. This is because the insidious onset of hypoxia can affect **Individual Readiness** and **Crew Capability** severely enough that **Task Performance** for critical tasks like piloting a vehicle may be affected and **Loss of Vehicle, Loss of Mission Objectives, or Loss of Mission** can occur.

## Hypoxia Integration with Other Risks:

The most obvious risks that are connected to the Hypoxia risk include DCS and EVA, because hypoxia is only nominally experienced by the crew due to operating in vehicle habitats to facilitate staged denitrogenation to reduce the time and resources to mitigate DCS prior to beginning EVA.

Because the crew will be living in a mildly hypoxic atmosphere, just about any physiological risk can be affected. The level of hypoxia associated with the Exploration Atmosphere is very mild and most risks are expected to not change significantly. Noted risks that will require some specific consideration, further research and/or operational surveillance include Sleep, SANS, Immune and Aerobic.
---
# SECTION V: Knowledge Base

## Decompression Sickness Knowledge Base
**Gaps in knowledge:** https://humanresearchroadmap.nasa.gov/schedules/?i=84

**EVA-201:** Characterize impacts of variable atmospheric conditions suits on human health and performance, including exploration atmospheres, variable pressure suits, and alternate prebreathe strategies.

**EVA-303:** Identify and test countermeasures related to exposure to variable atmospheric conditions.

**EVA-401:** Validate integrated EVA performance countermeasures related to optimizing physiological performance and minimizing DCS risk.

**State of Knowledge/Future work:** DCS is going to be a risk as long as there are pressure changes associated with spaceflight that can lead to tissue N2 supersaturation. Future DCS related research is documented in the Crew Health and Performance EVA Roadmap (Abercromby et al, 2020), which tends to be updated every 1-2 years.

## Hypoxia Knowledge Base
**Gaps in knowledge:** https://humanresearchroadmap.nasa.gov/schedules/?i=84

**EVA-201:** Characterize impacts of variable atmospheric conditions suits on human health and performance, including exploration atmospheres, variable pressure suits, and alternate prebreathe strategies.

**EVA-303:** Identify and test countermeasures related to exposure to variable atmospheric conditions.

**EVA-401:** Validate integrated EVA performance countermeasures related to optimizing physiological performance and minimizing DCS risk.

**State of Knowledge/Future work:** At this point, the physiological risk associated with hypoxic stress in planned exploration spaceflight atmospheres is expected to be well tolerated in order to gain the operational benefits associated with these reduced pressure atmospheres. Given that there is no analog on Earth that can mimic all relevant changes associated with spaceflight and these levels of hypobaric hypoxia, definitive research to close the risk is unavailable, therefore, an inflight monitoring plan to assess hypoxia symptoms during flight is required. Recommendations have been made and work will continue to ensure a robust health monitoring plan including measures of hypoxic stress is implemented. Any additional research will be documented in the Crew Health and Performance EVA Roadmap [239], which tends to be updated every 1-2 years.
---
The page is completely blank except for the page number "77" at the bottom right corner, which should be removed according to the transcription guidelines.
---
# SECTION VI: Conclusions

Decades of modeling and ground studies, as well as close collaboration with military research and other high-altitude testing have yielded an extremely successful DCS prevention architecture which has resulted in no decompression illness every requiring intervention or resulting in any injury that affected mission operations, crew status, or fitness for duty, whether it be during spaceflight or in training. Due to uncertainty in reporting, it is difficult to have equal confidence in stating no DCS ever occurred – but none was ever reported. This can be used as evidence that current practices are excessively conservative since NASA's DCS risk posture (NASA-STD-3001) does seem to provide room for the occasional DCS case. However, despite the time and consumables cost associated with current EVA PB protocols, these have not been too onerous or restrictive, and are acceptable give the ISS EVA rate of 2-6 EVAs per year, or even Shuttle's 2-4 EVAs per 2-week flight.

Plans for planetary surface exploration call for up to 24hr of EVA *per crew per week*. Such an increase in frequency requires a much more efficient PB protocol, and the increased exposures also increase the likelihood of observing a DCS event – before even accounting for whether planetary surface EVAs have an intrinsically higher risk of DCS. Thus, although current practices appear to be 100% effective in mitigating DCS risk during occasional microgravity EVAs, future surface EVAs represent a new type of exposure for which we lack experience. Ground studies are already underway to better characterize this risk, but it will also require novel technological advances to both prevent DCS (for example, Exploration Atmosphere habitats and variable pressure suits) as well as treatment capabilities to manage cases of DCS (such as high-pressure suits and airlocks that can maximize treatment pressures).

One arrow in the quiver of DCS prevention – minimizing cabin pressures – carries with it the risk of hypoxia. To prevent the cure from being worse than the disease, careful weighing of the risk associated with hypoxic atmospheres is critical. To be effective in reducing the risk of a possible DCS event, the crew will be subjected to a hypoxic stress for the duration of the mission segment where EVAs are conducted, as the habitat atmosphere will be slightly hypoxic. Thus, careful characterization of the impacts of hypobaric/hypoxic atmospheres is critical. Although the effects of reduced gravity cannot be simulated terrestrially – and there is no natural environment on Earth where alternate oxygen environments exist – long duration chamber studies can help close knowledge gaps by studying a variety of different pressure and oxygen compositions to understand the impact that living in these environments may have.

Since the spaceflight environment seeks to minimize both atmospheric pressure as well as oxygen content, hyperoxic exposures are extremely limited, such as during treatment for DCS, where both pressure, oxygen and time are maximized to eliminate any inert gas (nitrogen) bubbles and treat the inflammatory response associated with DCS. This has never occurred in flight, and although the risk of DCS during Exploration class EVAs may be higher than for current
---
ISS-based EVAs, any such treatment would happen with close monitoring and guidance by a medically trained specialist well versed in the risks of hyperoxia.

79
---
# REFERENCES

1. V. Harsch, "Robert Hooke, inventor of the vacuum pump and the first altitude chamber (1671)," *Aviat Space Environ Med*, vol. 77, pp. 867-9, Aug 2006.

2. P. Bert, *Barometric Pressure*. Bethesda, MD: Undersea Medical Society, Inc., 1878.

3. J. Fulton, *Decompression Sickness; Caisson Sickness, Diver's and Flier's Bends and Related Syndromes*. Philadephia, PA: Saunders, 1951.

4. E. Degner, K. Ikels, and T. Allen, "Dissolved nitrogen and bends in oxygen-nitrogen mixtures during exercise at decreased pressures," *Aerospace Medicine*, pp. 418-25, 1965.

5. M. T. Ryles and A. A. Pilmanis, "The initial signs and symptoms of altitude decompression sickness," *Aviat Space Environ Med*, vol. 67, pp. 983-9, Oct 1996.

6. P. K. Weathersby, L. D. Homer, and E. T. Flynn, "On the likelihood of decompression sickness," *J Appl Physiol Respir Environ Exerc Physiol*, vol. 57, pp. 815-25, Sep 1984.

7. L. Nims, "Enviromental factors affecting decompression sickness (Chapter 8)," in *Decompression Sickness*, J. Fulton, Ed., ed Philadelphia, PA: WB Saunders, 1951, pp. 192-222.

8. P. Tikuisis and W. Gerth, "Decompression Theory (Chapter 10.1)," in *Bennett and Elliotts' Physiology and Medicine of Diving*, A. O. Brubakk and T. S. Neuman, Eds., 5th ed New York: Saunders, 2002, pp. 419-54.

9. J. E. Blatteau, J. B. Souraud, E. Gempp, and A. Boussuges, "Gas nuclei, their origin, and their role in bubble formation," *Aviat Space Environ Med*, vol. 77, pp. 1068-76, Oct 2006.

10. P. K. Weathersby, L. D. Homer, and E. T. Flynn, "Homogeneous nucleation of gas bubbles in vivo," *J Appl Physiol Respir Environ Exerc Physiol*, vol. 53, pp. 940-6, Oct 1982.

11. A. Evans and D. N. Walder, "Significance of gas micronuclei in the aetiology of decompression sickness," *Nature*, vol. 222, pp. 251-2, Apr 19 1969.

12. K. G. Ikels, "Production of gas bubbles in fluids by tribonucleation," *Journal of Applied Physiology*, vol. 28, pp. 524-527, 1970.

13. R. D. Vann, J. Grimstad, and C. H. Nielsen, "Evidence for gas nuclei in decompressed rats," *Undersea Biomed Res*, vol. 7, pp. 107-12, Jun 1980.

14. B. A. Hills, *Decompression Sickness, Volume 1: The Biophysical Basis of Prevention and Treatment*. New York, NY: John Wiley & Sons, 1977.

15. E. Hemmingsen, "Nucleation of bubbles in vitro and in vivo," in *Supersaturation and bubble formation in fluid and organisms*, A. Brubakk, B. Hemmingsen, and G. Sundnes, Eds., ed Trondheim, Norway: Tapir Publishers, 1989, pp. 43-68.

16. B. D. Butler, T. Little, V. Cogan, and M. Powell, "Hyperbaric oxygen pre-breathe modifies the outcome of decompression sickness," *Undersea Hyperb Med*, vol. 33, pp. 407-17, Nov-Dec 2006.

17. R. Arieli, E. Boaron, and A. Abramovich, "Combined effect of denucleation and denitrogenation on the risk of decompression sickness in rats," *J Appl Physiol (1985)*, vol. 106, pp. 1453-8, Apr 2009.

18. A. Hayward, "Tribonucleation of bubbles," *British Journal of Applied Physics*, vol. 18, p. 641, 11/20 2002.
---
[19] P. M. McDonough and E. A. Hemmingsen, "Bubble formation in crabs induced by limb motions after decompression," *J Appl Physiol Respir Environ Exerc Physiol*, vol. 57, pp. 117-22, Jul 1984.

[20] P. M. McDonough and E. A. Hemmingsen, "A direct test for the survival of gaseous nuclei in vivo," *Aviat Space Environ Med*, vol. 56, pp. 54-6, Jan 1985.

[21] A. Brubakk, B. Hemmingsen, and G. Sundnes, *Supersaturation and bubble formation in fluids and organisms*. Trondheim, Norway: Tapir Publishers, 1989.

[22] A. O. Brubakk and T. S. Neuman, *Bennett and Elliott's physiology and medicine of diving*: Saunders Book Company, 2003.

[23] D. R. Williams and B. J. Johnson, "EMU shoulder injury tiger team report," Johnson Space Center, Houston, TX2003.

[24] D. T. Fitzpatrick and J. Conkin, "Improved pulmonary function in working divers breathing nitrox at shallow depths," *Aviat Space Environ Med*, vol. 74, pp. 763-7, Jul 2003.

[25] D. Horrigan Jr, L. CK, and C. J, "NASA requirements for underwater training and surface intervals before flying," in *39th Undersea and Hyperbaric Medical Society Workshop*, Bethesda, MD, 1989, pp. 11-27.

[26] R. D. Vann, P. Denoble, M. N. Emmerman, and K. S. Corson, "Flying after diving and decompression sickness," *Aviat Space Environ Med*, vol. 64, pp. 801-7, Sep 1993.

[27] N. Pollock and D. Fitzpatrick, "NASA flying after diving procedures," in *DAN flying after diving workshop proceedings*, Durham, NC, 2004, pp. 59-64.

[28] K. Thomas and H. McMann, *Spacesuits*, 2nd ed.: Springer Praxis, 2003.

[29] M. Powell, D. Horrigan Jr, W. JM, and W. Norfleet, "Extravehicular activities (chapter 6)," in *Space physiology and medicine*, A. Nicogossian, C. Huntoon-Leach, and S. Pool, Eds., 3rd ed Philadelphia, PA: Lea & Febiger, 1994, pp. 128-40.

[30] J. Locke, "Space environments (chapter 10)," in *Fundamentals of aerospace medicine*, J. Davis, R. Johnson, J. Stepanek, and J. Fogarty, Eds., 4th ed Philadelphia, PA: Lippincott Williams & Wilkins, 2008, pp. 270-2.

[31] J. Conkin, J. S. Klein, and K. E. Acock, "Description of 103 Cases of Hypobaric Sickness from NASA-sponsored Research," 2003.

[32] W. Hawkins and J. Zieglschmid, "Clinical aspects of crew safety (chapter 1)," in *Biomedical results of Apollo*, R. Johnson, L. Dietlein, and C. Berry, Eds., ed Washington DC: US Government Printing Office, 1975, p. 70.

[33] P. P. Foster and B. D. Butler, "Decompression to altitude: assumptions, experimental evidence, and future directions," *J Appl Physiol (1985)*, vol. 106, pp. 678-90, Feb 2009.

[34] G. A. Bendrick, M. J. Ainscough, A. A. Pilmanis, and R. U. Bisson, "Prevalence of decompression sickness among U-2 pilots," *Aviat Space Environ Med*, vol. 67, pp. 199-206, Mar 1996.

[35] G. L. Hundemer, S. L. Jersey, R. P. Stuart, W. P. Butler, and A. A. Pilmanis, "Altitude decompression sickness incidence among U-2 pilots: 1994-2010," *Aviat Space Environ Med*, vol. 83, pp. 968-74, Oct 2012.

[36] W. Meader, "Decompression sickness in high-altitude flight," *Aerospace Medicine*, vol. 38, pp. 31-3, 1967.
---
[37] J. T. Webb, M. D. Fischer, C. L. Heaps, and A. A. Pilmanis, "Exercise-enhanced preoxygenation increases protection from decompression sickness," *Aviat Space Environ Med*, vol. 67, pp. 618-24, Jul 1996.

[38] T. C. Hankins, J. T. Webb, G. C. Neddo, A. A. Pilmanis, and W. J. Mehm, "Test and evaluation of exercise-enhanced preoxygenation in U-2 operations," *Aviat Space Environ Med*, vol. 71, pp. 822-6, Aug 2000.

[39] S. L. Jersey, R. T. Baril, R. D. McCarty, and C. M. Millhouse, "Severe neurological decompression sickness in a U-2 pilot," *Aviat Space Environ Med*, vol. 81, pp. 64-8, Jan 2010.

[40] J. Conkin, "Evidence-based approach to the analysis of serious decompression sickness with application to EVA astronauts," National Aeronautics and Space Administration, Lyndon B. Johnson Space Center2001.

[41] J. M. Waligora, D. Horrigan Jr, J. Conkin, and A. Hadley III, "Verification of an altitude decompression sickness prevention protocol for Shuttle operations utilizing a 10.2 psi pressure stage," 1984.

[42] J. Conkin, B. Edwards, J. Waligora, J. Stanford Jr, J. Gilbet III, and D. Horrigan Jr, "Updating empirical models that predict the incidence of aviator decompression sickness and venous gas emboli for shuttle and space station extravehicular operations," 1990.

[43] M. Powell, W. Norfleet, J. Waligora, K. V. Kumar, R. Robinson, and B. Butler, "Modifications of Physiological Processes Concerning Extravehicular Activity in Microgravity," *SAE Transactions*, vol. 103, pp. 739-748, 1994.

[44] M. L. Gernhardt, J. Conkin, R. D. Vann, N. W. Pollock, and A. H. Feiveson, "DCS RISKS IN GROUND-BASED HYPOBARIC TRIALS VS. EXTRAVEHICULAR ACTIVITY," *Undersea Hyperbaric Medicine*, vol. 31, p. G100, 2004.

[45] J. Conkin, H. G. Sung, and A. H. Feiveson, "A latent class model to assess error rates in diagnosis of altitude decompression sickness," *Aviat Space Environ Med*, vol. 77, pp. 816-24, Aug 2006.

[46] J. M. Waligora and L. J. Pepper, "Physiological Experience During Shuttle EVA," 1995.

[47] J. M. Waligora and K. V. Kumar, "Energy utilization rates during shuttle extravehicular activities," *Acta Astronaut*, vol. 36, pp. 595-9, Oct-Dec 1995.

[48] A. E. Nicogossian and J. F. Parker, *Space Physiology and Medicine*: NASA, 1982.

[49] U. I. Balldin, "Effects of ambient temperature and body position on tissue nitrogen elimination in man," *Aerosp Med*, vol. 44, pp. 365-70, Apr 1973.

[50] D. Pendergast and A. Olszowka, "Effect of exercise, thermal state, blood flow on inert gas exchange," in *38th Undersea and Hyperbaric Medical Society Workshop*, Bethesda, MD, 1989, pp. 37-57.

[51] R. Margaria and J. Sendroy, Jr., "Effect of carbon dioxide on rate of denitrogenation in human subjects," *J Appl Physiol*, vol. 3, pp. 295-308, Dec 1950.

[52] H. Jones, E. Myers, and W. Berg, "Gas exchange, circulation, and diffusion," National Research Council, Washington DCApril 10, 1945 1945.

[53] A. R. Behnke, R. M. Thomson, and L. A. Shaw, "The rate of elimination of dissolved nitrogen in man in relation to the fat and water content of the body," *American Journal of Physiology-Legacy Content*, vol. 114, pp. 137-146, 1935.
---
[54] A. Behnke, "The application of measurements of nitrogen elimination to the problem of decompressing divers," *US Nav. Med. Bull*, vol. 35, pp. 219-240, 1937.

[55] A. Behnke and T. Willmon, "Gaseous nitrogen and helium elimination from the body during rest and exercise," *American Journal of Physiology-Legacy Content*, vol. 131, pp. 619-626, 1940.

[56] U. Balldin, C. Lundgren, J. Lundvall, and S. Mellander, "Changes in the elimination of 133 xenon from the anterior tibial muscle in man induced by immersion in water and by shifts in body position," *Aerospace medicine*, vol. 42, pp. 489-493, 1971.

[57] U. I. Balldin and C. E. Lundgren, "Effects of immersion with the head above water on tissue nitrogen elimination in man," *Aerosp Med*, vol. 43, pp. 1101-8, Oct 1972.

[58] U. I. Balldin, "Effects of immersion and ambient temperature on elimination of 133 xenon from human adipose tissue," in *6th symposium on underwater physiology*, Bethesda, MD, 1978, pp. 329-34.

[59] C. Theis, J. Adams, and K. Stevens, "Nitrogen washout in the supine position," *Aerospace Medical Association Preprints*, pp. 262-3, 1979.

[60] U. I. Balldin and P. Borgström, "Intracardial gas bubbles of altitude after negative pressure breathing," *Aviat Space Environ Med*, vol. 48, pp. 1007-11, Nov 1977.

[61] T. B. Curry and C. E. Lundgren, "Negative pressure breathing enhances nitrogen elimination," *Aviation, space, and environmental medicine*, vol. 74, pp. 1034-1039, 2003.

[62] W. A. Gerth, R. D. Vann, N. E. Leatherman, and M. D. Feezor, "Effects of microgravity on tissue perfusion and the efficacy of astronaut denitrogenation for EVA," *Aviation, Space, and Environmental Medicine*, vol. 58, pp. A100-5, 1987.

[63] W. Gerth, R. D. Vann, and N. E. Leatherman, "Whole-body nitrogen elimination during oxygen prebreathing and altitude decompression sickness risk," in *38th Undersea and Hyperbaric Medical Society Workshop*, Bethesda, MD, 1989, pp. 147-51.

[64] R. D. Vann and W. A. Gerth, "Factors affecting tissue perfusion and the efficacy of astronaut denitrogenation for extravehicular activity," *FG Hall Hypo/Hyperbaric Center, Duke Medical Center: Durham, NC. Final Report on NASA Contract NAG*, pp. 9-134, 1995.

[65] J. Waligora, D. Horrigan Jr, and J. Conkin, "Effect of hydration on nitrogen washout in human subjects," 1983.

[66] M. Powell, J. Waligora, and W. Norfleet, "Decompression in Simulated Microgravity: Bed Rest and its Influence on Stress-Assisted Nucleation," *Undersea Biomedical Research*, vol. 19, p. 54, 1992.

[67] J. Conkin and M. R. Powell, "Lower body adynamia as a factor to reduce the risk of hypobaric decompression sickness," *Aviation, space, and environmental medicine*, vol. 72, pp. 202-214, 2001.

[68] A. Groom and L. Farhi, "Cutaneous diffusion of atmospheric N2 during N2 washout in the dog," *Journal of Applied Physiology*, vol. 22, pp. 740-745, 1967.

[69] A. Barer, S. Filipenkov, V. Katuntsev, L. Vogt, and J. Wenzel, "The feasibility of Doppler monitoring during EVA," *Acta Astronautica*, vol. 36, pp. 81-83, 1995.

[70] J. Conkin, P. Foster, M. Powell, and J. Waligora, "Relationship of the time course of venous gas bubbles to altitude decompression illness," *Undersea & hyperbaric medicine: journal of the Undersea and Hyperbaric Medical Society, Inc*, vol. 23, pp. 141-149, 1996.

83
---
[71] J. Conkin, P. P. Foster, and M. R. Powell, "Evolved gas, pain, the power law, and probability of hypobaric decompression sickness," *Aviation, space, and environmental medicine*, vol. 69, pp. 352-359, 1998.

[72] K. C. Loftin, J. Conkin, and M. R. Powell, "Modeling the effects of exercise during 100% oxygen prebreathe on the risk of hypobaric decompression sickness," *Aviation, space, and environmental medicine*, vol. 68, pp. 199-204, 1997.

[73] D. Pendergast, C. Senf, and C. Lundgren, "Is the rate of whole-body nitrogen elimination influenced by exercise?," *Undersea & Hyperbaric Medicine*, vol. 39, p. 595, 2012.

[74] J. Conkin, M. L. Gernhardt, and J. Wessel, "Exploiting Aerobic Fitness to Reduce Risk of Hypobaric Decompression Sickness," in *Undersea and Hyperbaric Medical Society annual meeting*, 2007.

[75] N. Pollock, M. Natoli, R. Vann, R. Nishi, P. Sullivan, M. Gernhardt, *et al.*, "High altitude DCS risk is greater for low fit individuals completing oxygen prebreathe based on relative intensity exercise prescriptions.[Abstract# 50]," *Aviat Space Environ Med*, vol. 74, p. B11, 2004.

[76] J. Conkin, M. L. Gernhardt, M. R. Powell, and N. Pollock, "A probability model of decompression sickness at 4.3 psia after exercise prebreathe," 2004.

[77] J. Conkin, "Analysis of NASA decompression sickness and venous gas emboli data and gender (Chapter 3)," in *Women and pressure.*, C. Fife and M. St. Leger Dowse, Eds., ed Flagstaff, AZ: Best Publishing Co, 2010, pp. 41-68.

[78] D. Carturan, A. Boussuges, H. Burnet, J. Fondarai, P. Vanuxem, and B. Gardette, "Circulating venous bubbles in recreational diving: relationships with age, weight, maximal oxygen uptake and body fat percentage," *Int J Sports Med*, vol. 20, pp. 410-4, Aug 1999.

[79] D. Carturan, A. Boussuges, P. Vanuxem, A. Bar-Hen, H. Burnet, and B. Gardette, "Ascent rate, age, maximal oxygen uptake, adiposity, and circulating venous bubbles after diving," *J Appl Physiol (1985)*, vol. 93, pp. 1349-56, Oct 2002.

[80] J. T. Webb, A. A. Pilmanis, U. I. Balldin, and J. R. Fischer, "Altitude decompression sickness susceptibility: influence of anthropometric and physiologic variables," *Aviation, space, and environmental medicine*, vol. 76, pp. 547-551, 2005.

[81] J. Conkin, M. R. Powell, and M. L. Gernhardt, "Age affects severity of venous gas emboli on decompression from 14.7 to 4.3 psia," *Aviat Space Environ Med*, vol. 74, pp. 1142-50, Nov 2003.

[82] J. M. Waligora, D. J. Horrigan, Jr., and J. Conkin, "The effect of extended O2 prebreathing on altitude decompression sickness and venous gas bubbles," *Aviat Space Environ Med*, vol. 58, pp. A110-2, Sep 1987.

[83] J. Webb, H. Ryder, G. Engel, J. Romano, M. Blankenhorn, and E. Ferris, "The effect on susceptibility to decompression sickness of preflight oxygen inhalation at rest as compared to oxygen inhalation during strenuous exercise," National Research Counil, Washington DC1943.

[84] W. Boothby, U. Luft, and O. Benson Jr, "Gaseous nitrogen elimination; experiments when breathing oxygen at rest and at work with comments on dysbarism," *Journal of aviation medicine*, vol. 23, pp. 141-58; 176, 1952.
---
[85] J. T. Webb, G. A. Dixon, and J. F. Wiegman, "Potential for Reduction of Decompression Sickness By Prebreathing With 100% Oxygen While Exercising," SAE Technical Paper 0148-7191, 1989.

[86] J. T. Webb and A. A. Pilmanis, "A new preoxygenation procedure for extravehicular activity (EVA)," *Acta astronautica*, vol. 42, pp. 115-122, 1998.

[87] T. C. Hankins, J. T. Webb, G. C. Neddo, A. A. Pilmanis, and W. J. Mehm, "Test and evaluation of exercise-enhanced preoxygenation in U-2 operations," *Aviation, space, and environmental medicine*, vol. 71, pp. 822-826, 2000.

[88] J. T. Webb, A. A. Pilmanis, M. D. Fischer, and N. Kannan, "Enhancement of preoxygenation for decompression sickness protection: effect of exercise duration," WYLE LABS LIFE SCIENCES AND SERVICES INC SAN ANTONIO TX2002.

[89] J. T. Webb, A. A. Pilmanis, and U. I. Balldin, "Altitude decompression sickness at 7620 m following prebreathe enhanced with exercise periods," *Aviation, space, and environmental medicine*, vol. 75, pp. 859-864, 2004.

[90] M. Gernhardt, J. Conkin, P. Foster, A. Pilmanis, B. Butler, C. Fife, *et al.*, "Design of a 2-hours prebreathe protocol for space walks from the International Space Station," *Aviat Space Environ Med*, vol. 71, p. 277, 2000.

[91] M. Gernhardt, J. Dervay, J. Welch, J. Conkin, K. Acock, S. Lee, *et al.*, "Implementation of an exercise prebreathe protocol for construction and maintenance of the international space station: results to date," *Aviat Space Environ Med*, vol. 74, p. 397, 2003.

[92] T. Allen, D. Maio, S. Beard, and R. Bancroft, "Space-cabin and suit pressures for avoidance of decompression sickness and alleviation of fire hazard," *Journal of Applied Physiology*, vol. 27, pp. 13-17, 1969.

[93] D. A. Maio, T. H. Allen, and R. W. Bancroft, "Decompression sickness and measured levels of exercise on simulated Apollo missions," *Aerospace medicine*, vol. 41, pp. 1162-1165, 1970.

[94] J. Cooke and W. Robertson, "Decompression sickness in simulated Apollo-Soyuz space missions," *Aerospace medicine*, vol. 45, 1974.

[95] D. Horrigan and J. Waligora, "The development of effective procedures for the protection of space shuttle crews against decompression sickness during extravehicular activities," in *Proceedings of the 1980 Aerospace Medical Association Annual Scientific Meeting, Anaheim, CA*, 1980, pp. 14-5.

[96] M. Damato, F. Highly, E. Hendler, and E. Michel, "Rapid decompression hazards after prolonged exposure to 50 per cent oxygen-50 per cent nitrogen atmosphere," *Aerospace medicine*, vol. 34, pp. 1037-1040, 1963.

[97] R. D. Vann and J. R. Torre-Bueno, "A theoretical method for selecting space craft and space suit atmospheres," *Aviat Space Environ Med*, vol. 55, pp. 1097-102, Dec 1984.

[98] B. A. Hills, "Compatible atmospheres for a space suit, space station, and shuttle based on physiological principles," *Aviat Space Environ Med*, vol. 56, pp. 1052-8, Nov 1985.

[99] D. Horrigan Jr, J. Waligora, and D. Nachtwey, "Physiological considerations for EVA in the Space Station era," 1985.

[100] J. M. Waligora, D. J. Horrigan, Jr., M. W. Bungo, and J. Conkin, "Investigation of the combined effects of bedrest and mild hypoxia," *Aviat Space Environ Med*, vol. 53, pp. 643-6, Jul 1982.
---
[101] J. Adams, "Preventing of bends during space Shuttle EVA's using stage decompression," in *Preprints of the 1981 Aerospace Medical Association Meeting*, 1981.

[102] D. A. Maio, T. H. Allen, and R. W. Bancroft, "Decompression sickness in simulated Apollo space-cabins," *Aerospace medicine*, vol. 40, pp. 1114-1118, 1969.

[103] M. P. Spencer, "Decompression limits for compressed air determined by ultrasonically detected blood bubbles," *J Appl Physiol*, vol. 40, pp. 229-35, Feb 1976.

[104] T. Neuman, D. Hall, and P. Linaweaver Jr, "Gas phase separation during decompression in man: ultrasound monitoring," *Undersea biomedical research*, vol. 3, pp. 121-130, 1976.

[105] J. Adams, R. Olson, and G. Dixon, "Use of the Doppler precordial bubble detector in altitude decompressions," *Proc, Aerosp, Med. Assoc. Washington, DC*, pp. 260-261, 1979.

[106] T. Allen, D. Maio, and R. Bancroft, "Body fat, denitrogenation and decompression sickness in men exercising after abrupt exposure to altitude," *Aerospace medicine*, vol. 42, pp. 518-524, 1971.

[107] K. M. Krause and A. A. Pilmanis, "The effectiveness of ground level oxygen treatment for altitude decompression sickness in human research subjects," *Aviation, space, and environmental medicine*, vol. 71, pp. 115-118, 2000.

[108] J. P. Cooke, R. R. Bollinger, and B. Richardson, "Prevention of decompression sickness during a simulated space docking mission," *Aviat Space Environ Med*, vol. 46, pp. 930-3, Jul 1975.

[109] A. A. Pilmanis, J. T. Webb, N. Kannan, and U. Balldin, "The effect of repeated altitude exposures on the incidence of decompression sickness," *Aviat Space Environ Med*, vol. 73, pp. 525-31, Jun 2002.

[110] K. V. Kumar, J. M. Waligora, and J. H. Gilbert, 3rd, "The influence of prior exercise at anaerobic threshold on decompression sickness," *Aviat Space Environ Med*, vol. 63, pp. 899-904, Oct 1992.

[111] K. V. Kumar, J. M. Waligora, and M. R. Powell, "Epidemiology of decompression sickness under simulated space extravehicular activities," *Aviat Space Environ Med*, vol. 64, pp. 1032-9, Nov 1993.

[112] R. Vann and W. Gerth, "Is the risk of DCS in microgravity less than on earth?[Abstract# 45]," *Aviat Space Environ Med*, vol. 68, p. A8, 1997.

[113] J. T. Webb, L. P. Krock, and M. L. Gernhardt, "Oxygen consumption at altitude as a risk factor for altitude decompression sickness," *Aviat Space Environ Med*, vol. 81, pp. 987-92, Nov 2010.

[114] U. I. Balldin, A. A. Pilmanis, and J. T. Webb, "The effect of simulated weightlessness on hypobaric decompression sickness," *Aviation, space, and environmental medicine*, vol. 73, pp. 773-778, 2002.

[115] J. T. Webb, D. P. Beckstrand, A. A. Pilmanis, and U. I. Balldin, "Decompression sickness during simulated extravehicular activity: ambulation vs. non-ambulation," *Aviation, space, and environmental medicine*, vol. 76, pp. 778-781, 2005.

[116] N. Pollock, M. Natoli, J. Conkin, J. W. III, and M. Gernhardt, "Ambulation increases decompression sickness in altitude exposure," in *2015 Annual Scientific Meeting of the Aerospace Medical Association, Lake Buena Vista, Florida, May*, 2015, pp. 10-14.
---
[117] J. Conkin, N. W. Pollock, M. J. Natoli, S. D. Martina, J. H. Wessel, and M. L. Gernhardt, "Venous gas emboli and ambulation at 4.3 psia," *Aerospace Medicine and Human Performance*, vol. 88, pp. 370-376, 2017.

[118] J. Bateman, "Preoxygenation and nitrogen elimination (Chapter 9). Part I: Review of data on value of preoxygenation in prevention of decompression sickness," in *Decompression Sickness*, J. Fulton, Ed., ed Philadelphia: WB Saunders, 1951, pp. 242-77.

[119] J. Stepanek and J. T. Webb, "Physiology of decompressive stress (Chapter 3)," in *Fundamentals of aerospace medicine*, J. Davis, R. Johnson, J. Stepanek, and J. Fogarty, Eds., 4th ed Philadelphia, PA: Lippincott Williams & Wilkins, 2008.

[120] A. Pilmanis, "The proceedings of the 1990 hypobaric decompression sickness workshop," Brooks Air Force Base, TX: Air Force Systems Command, 1992.

[121] R. G. McIver, S. E. Beard, R. W. Bancroft, and T. H. Allen, "Treatment of decompression sickness in simulated space flight," *Aerosp Med*, vol. 38, pp. 1034-6, Oct 1967.

[122] R. Clarke, F. Humm, and L. Nims, "The efficacy of preflight denitrogenation in the prevention of decompression sickness," National Research Council, Committee on Medical Research, Yale Aeromedical Research Unit, Yale University, New Haven CT1945.

[123] J. P. Cooke, "Denitrogenation interruptions with air," *Aviat Space Environ Med*, vol. 47, pp. 1205-9, 1976.

[124] J. D. Adams, C. Theis, and K. Stevens, "Denitrogenation/renitrogenation profiles: interruption of oxygen prebreathing," in *Aerospace Medical Association Annual Scientific Meeting*, Las Vegas, NV, 1977, pp. 42-3.

[125] D. Horrigan Jr, C. Wells, G. Hart, and J. Goodpasture, "The uptake and depletion of inert gases in muscle and subcutaneous tissues of human subjects," in *Proceedings of the 1979 Aerospace Medical Association Annual Scientific Meeting*, Washington DC, 1979, pp. 264-5.

[126] G. Dixon, J. Adams, R. Olson, and E. Fitzpatrick, "Validation of additional prebreathing times for air interruptions in the shuttle EVA prebreathing profile," in *Proceedings of the 1980 Aerospace Medical Association Annual Scientific Meeting*, Anaheim, CA, 1980, pp. 16-7.

[127] A. Barer, M. Vakar, G. VOROBYEV, L. Iseyev, S. Filipenkov, and V. Chadov, "Influence of addition of nitrogen to inhaled oxygen on efficacy of two-hour denitrogenation before decompression from 760 to 220 mm Hg," *Kosmich. Biol. i Aviakosmich. Med.,(Moscow)*, vol. 17, pp. 45-47, 1983.

[128] A. A. Pilmanis, J. T. Webb, U. I. Balldin, J. Conkin, and J. R. Fischer, "Air break during preoxygenation and risk of altitude decompression sickness," *Aviat Space Environ Med*, vol. 81, pp. 944-50, Oct 2010.

[129] A. Andersen and L. Hillestad, "Hemodynamic responses to oxygen breathing and the effect of pharmacological blockade," *Acta Med Scand*, vol. 188, pp. 419-24, Nov 1970.

[130] D. Anderson, G. Nagasawa, W. Norfleet, A. Olszowka, and C. Lundgren, "O2 pressures between 0.12 and 2.5 atm abs, circulatory function, and N2 elimination," *Undersea Biomed Res*, vol. 18, pp. 279-92, Jul 1991.

[131] H. D. Van Liew, J. Conkin, and M. E. Burkard, "The oxygen window and decompression bubbles: estimates and significance," *Aviat Space Environ Med*, vol. 64, pp. 859-65, Sep 1993.
---
[132] J. Conkin, "Decompression sickness after air break in prebreathe described with a survival model," *Aviat Space Environ Med*, vol. 82, pp. 589-98, Jun 2011.

[133] H. Adler, "Dysbarism. Aeromedical Review 1-64," 1964.

[134] D. Fryer and H. Roxburgh, "Decompression sickness (Chapter 8)," in *A textbook of aviation physiology*, J. Gillies, Ed., ed New York: Pergamon Press, 1965, pp. 122-51.

[135] J. Conkin, A. A. Pilmanis, and J. T. Webb, "Case Descriptions and Observations About Cutis Marmorata From Hypobaric Decompressions," NASA Johnson Space Center2002.

[136] J. T. Webb and A. A. Pilmanis, "Breathing 100% oxygen compared with 50% oxygen: 50% nitrogen reduces altitude-induced venous gas emboli," *Aviation, space, and environmental medicine*, vol. 64, pp. 808-812, 1993.

[137] C. W. Flugel, J. J. Kosmo, and J. R. Rayfield, "Development of a zero-prebreathe spacesuit," SAE Technical Paper 0148-7191, 1984.

[138] J. T. Webb, R. M. Olson, R. W. Krutz, Jr., G. Dixon, and P. T. Barnicott, "Human tolerance to 100% oxygen at 9.5 psia during five daily simulated 8-hour EVA exposures," *Aviat Space Environ Med*, vol. 60, pp. 415-21, May 1989.

[139] G. A. Dixon, J. D. Adams, and W. T. Harvey, "Decompression sickness and intravenous bubble formation using a 7.8 psia simulated pressure-suit environment," *Aviat Space Environ Med*, vol. 57, pp. 223-8, Mar 1986.

[140] G. A. Dixon, R. W. Krutz, Jr., and J. R. Fischer, "Decompression sickness and bubble formation in females exposed to a simulated 7.8 psia suit environment," *Aviat Space Environ Med*, vol. 59, pp. 1146-9, Dec 1988.

[141] J. T. Webb, K. W. Smead, J. R. Jauchem, and P. T. Barnicott, "Blood factors and venous gas emboli: surface to 429 mmHg (8.3 psi)," *Undersea Biomed Res*, vol. 15, pp. 107-21, Mar 1988.

[142] K. W. Smead, G. A. Dixon, J. T. Webb, and R. W. Krutz Jr, "Decompression sickness and venous gas emboli at 8.3 psia," in *SAFE Association*, 1987.

[143] G. A. Dixon and R. W. Krutz, Jr., "Evaluation of 9.5 psia as a suit pressure for prolonged extravehicular activity," in *SAFE 23rd Annual Symposium*, Van Nuys, CA, 1985, pp. 122-5.

[144] K. V. Kumar, J. M. Waligora, and D. S. Calkins, "Threshold altitude resulting in decompression sickness," *Aviat Space Environ Med*, vol. 61, pp. 685-9, Aug 1990.

[145] J. T. Webb, A. A. Pilmanis, and R. B. O'Connor, "An abrupt zero-preoxygenation altitude threshold for decompression sickness symptoms," *Aviat Space Environ Med*, vol. 69, pp. 335-40, Apr 1998.

[146] V. M. Voge, "Probable bends at 14,000 feet: a case report," *Aviat Space Environ Med*, vol. 60, pp. 1102-3, Nov 1989.

[147] F. W. Rudge, "A case of decompression sickness at 2,437 meters (8,000 feet)," *Aviat Space Environ Med*, vol. 61, pp. 1026-7, Nov 1990.

[148] S. Cook, "Part II. Role of exercise, temperature, drugs, and water balance in decompression sickness (Chapter 8)," in *Decompression sicness*, J. Fulton, Ed., ed Philadelphia, PA: WB Saunders, 1951, pp. 223-35.

[149] J. T. Webb, T. R. Morgan, and S. D. Sarsfield, "Altitude Decompression Sickness Risk and Physical Activity During Exposure," *Aerosp Med Hum Perform*, vol. 87, pp. 516-20, Jun 2016.
---
[150] J. Conkin, J. M. Waligora, D. J. Horrigan Jr, and A. T. Hadley III, "The effect of exercise on venous gas emboli and decompression sickness in human subjects at 4.3 psia," 1987.

[151] F. M. Henry, "Effects of exercise and altitude on the growth and decay of aviator's bends," *J Aviat Med*, vol. 27, pp. 250-9, Jun 1956.

[152] M. R. Powell, J. M. Waligora, W. T. Norfleet, and K. V. Kumar, "Project Argo: gas phase formation in simulated microgravity," 1993.

[153] R. W. Krutz, Jr. and G. A. Dixon, "The effects of exercise on bubble formation and bends susceptibility at 9,100 m (30,000 ft; 4.3 psia)," *Aviat Space Environ Med*, vol. 58, pp. A97-9, Sep 1987.

[154] M. R. Powell, J. Waligora, and K. V. Kumar, "Decompression Gas Phase Formation in Simulated Null Gravity," *SAE Transactions*, vol. 104, pp. 834-841, 1995.

[155] D. M. Whitaker, L. R. Blinks, W. E. Berg, V. C. Twitty, and M. Harris, "MUSCULAR ACTIVITY AND BUBBLE FORMATION IN ANIMALS DECOMPRESSED TO SIMULATED ALTITUDES," *J Gen Physiol*, vol. 28, pp. 213-23, Jan 20 1945.

[156] J. P. Dervay, M. R. Powell, B. Butler, and C. E. Fife, "The effect of exercise and rest duration on the generation of venous gas bubbles at altitude," *Aviat Space Environ Med*, vol. 73, pp. 22-7, Jan 2002.

[157] H. D. Van Liew and S. Raychaudhuri, "Stabilized bubbles in the body: pressure-radius relationships and the limits to stabilization," *J Appl Physiol (1985)*, vol. 82, pp. 2045-53, Jun 1997.

[158] H. Van Liew, "Evidence that breathing of oxygen inactivates precursors if decompression bubbles.[Abstract# 8]," *Undersea Hyperbaric Med*, vol. 25, p. 11, 1998.

[159] H. Van Liew and J. Conkin, "A Start Toward Micronucleus-Based Decompression Models; Altitude Decompression," in *Undersea and Hyperbaric Medical Society Annual Meeting*, 2007, p. 13.

[160] Z. Dujić, I. Palada, Z. Valic, D. Duplancić, A. Obad, U. Wisløff, et al., "Exogenous nitric oxide and bubble formation in divers," *Med Sci Sports Exerc*, vol. 38, pp. 1432-5, Aug 2006.

[161] Z. Valic, I. Palada, and Z. Dujic, "Short-acting NO donor and decompression sickness in humans," *J Appl Physiol (1985)*, vol. 102, p. 1725; author reply 1726, Apr 2007.

[162] U. Wisløff, R. S. Richardson, and A. O. Brubakk, "Exercise and nitric oxide prevent bubble formation: a novel approach to the prevention of decompression sickness?," *J Physiol*, vol. 555, pp. 825-9, Mar 16 2004.

[163] A. F. Abercromby, M. L. Gernhardt, and J. Conkin, "Potential benefit of intermittent recompression in reducing decompression stress during lunar extravehicular activities," *Aviation Space and Environmental Medicine*, vol. 79, p. 425, 2008.

[164] A. F. Abercromby, J. Conkin, and M. L. Gernhardt, "Modeling a 15-min extravehicular activity prebreathe protocol using NASA's exploration atmosphere (56.5 kPa/34% O 2)," *Acta Astronautica*, vol. 109, pp. 76-87, 2015.

[165] A. Mollerlokken, C. Gutvik, V. J. Berge, A. Jorgensen, A. Loset, and A. O. Brubakk, "Recompression during decompression and effects on bubble formation in the pig," *Aviat Space Environ Med*, vol. 78, pp. 557-60, Jun 2007.

[166] P. K. Weathersby, "Individual susceptibility to DCS," in *38th Undersea and Hyperbaric Medical Society Workshop*, Bethesda, MD, 1989, pp. 372-3.
---
[167] K. V. Kumar, D. S. Calkins, J. M. Waligora, J. H. Gilbert, 3rd, and M. R. Powell, "Time to detection of circulating microbubbles as a risk factor for symptoms of altitude decompression sickness," *Aviat Space Environ Med*, vol. 63, pp. 961-4, Nov 1992.

[168] J. Law and S. Watkins, "Individual susceptibility to hypobaric environments: an update," 2010.

[169] R. G. Eckenhoff, C. S. Olstad, and G. Carrod, "Human dose-response relationship for decompression and endogenous bubble formation," *J Appl Physiol (1985)*, vol. 69, pp. 914-8, Sep 1990.

[170] B. A. Cameron, C. S. Olstad, J. M. Clark, R. Gelfand, E. A. Ochroch, and R. G. Eckenhoff, "Risk factors for venous gas emboli after decompression from prolonged hyperbaric exposures," *Aviat Space Environ Med*, vol. 78, pp. 493-9, May 2007.

[171] Z. M. Sulaiman, A. A. Pilmanis, R. B. O'Connor, and F. Baumgardner, "Relationship between Age and Susceptibility to Decompression Sickness. A Review," C. S. Directorate, Ed., ed. Brooks Air Force Base: DTIC Document, 1995.

[172] N. A. Schellart, T. P. Vellinga, F. J. van Dijk, and W. Sterk, "Doppler bubble grades after diving and relevance of body fat," *Aviat Space Environ Med*, vol. 83, pp. 951-7, Oct 2012.

[173] M. J. Saary and G. W. Gray, "A review of the relationship between patent foramen ovale and type II decompression sickness," *Aviat Space Environ Med*, vol. 72, pp. 1113-20, Dec 2001.

[174] P. P. Foster, A. M. Boriek, B. D. Butler, M. L. Gernhardt, and A. A. Bové, "Patent foramen ovale and paradoxical systemic embolism: a bibliographic review," *Aviat Space Environ Med*, vol. 74, pp. B1-64, Jun 2003.

[175] J. T. Webb, N. Kannan, and A. Pilmanis, "Gender not a factor for altitude decompression sickness risk," *Aviation, space, and environmental medicine*, vol. 74, pp. 2-10, 2003.

[176] L. A. Thompson, R. S. Chhikara, and J. Conkin, "Cox Proportional Hazards Models for Modeling the Time to Onset of Decompression Sickness in Hypobaric Environments," 2003.

[177] F. W. Rudge, "Relationship of menstrual history to altitude chamber decompression sickness," *Aviat Space Environ Med*, vol. 61, pp. 657-9, Jul 1990.

[178] Z. Dujic, D. Duplancic, I. Marinovic-Terzic, D. Bakovic, V. Ivancev, Z. Valic, *et al.*, "Aerobic exercise before diving reduces venous gas bubble formation in humans," *J Physiol*, vol. 555, pp. 637-42, Mar 16 2004.

[179] Z. Dujic, Z. Valic, and A. O. Brubakk, "Beneficial role of exercise on scuba diving," *Exerc Sport Sci Rev*, vol. 36, pp. 38-42, Jan 2008.

[180] J. T. Webb, A. A. Pilmanis, U. I. Balldin, and J. R. Fischer, "Altitude decompression sickness susceptibility: influence of anthropometric and physiologic variables," *Aviat Space Environ Med*, vol. 76, pp. 547-51, Jun 2005.

[181] A. Fahlman and D. M. Dromsky, "Dehydration effects on the risk of severe decompression sickness in a swine model," *Aviat Space Environ Med*, vol. 77, pp. 102-6, Feb 2006.

[182] K. V. Kumar and M. R. Powell, "Survivorship models for estimating the risk of decompression sickness," *Aviat Space Environ Med*, vol. 65, pp. 661-5, Jul 1994.

[183] R. Nishi, "Doppler and ultrasonic bubble detection (Chapter 15)," in *The physiology and medicine of diving*, P. Bennett and D. Elliott, Eds., ed Philadelphia, PA: WB Saunders, 1993, pp. 433-53.
---
[184] A. A. Pilmanis, U. I. Balldin, J. T. Webb, and K. M. Krause, "Staged decompression to 3.5 psi using argon-oxygen and 100% oxygen breathing mixtures," *Aviat Space Environ Med*, vol. 74, pp. 1243-50, Dec 2003.

[185] O. S. Eftedal, H. Tjelmeland, and A. O. Brubakk, "Validation of decompression procedures based on detection of venous gas bubbles: A Bayesian approach," *Aviat Space Environ Med*, vol. 78, pp. 94-9, Feb 2007.

[186] K. V. Kumar and J. M. Waligora, "Efficacy of Doppler ultrasound [correction of utrasound] for screening symptoms of decompression sickness during simulated extravehicular activities," *Acta Astronaut*, vol. 36, pp. 589-93, Oct-Dec 1995.

[187] U. I. Balldin, A. A. Pilmanis, and J. T. Webb, "Central nervous system decompression sickness and venous gas emboli in hypobaric conditions," *Aviation, Space, and Environmental Medicine*, vol. 75, pp. 969-972, 2004.

[188] H. D. Van Liew and M. E. Burkard, "Density of decompression bubbles and competition for gas among bubbles, tissue, and blood," *J Appl Physiol (1985)*, vol. 75, pp. 2293-301, Nov 1993.

[189] H. D. Van Liew and M. E. Burkard, "Simulation of gas bubbles in hypobaric decompressions: roles of O2, CO2, and H2O," *Aviat Space Environ Med*, vol. 66, pp. 50-5, Jan 1995.

[190] H. D. Van Liew and M. E. Burkard, "Simulation of gas bubbles and the role of O2, CO2, and H2O," *Undersea Hyperb Med*, vol. 21, p. 20, 1994.

[191] R. M. Olson, R. W. Krutz, Jr., G. A. Dixon, and K. W. Smead, "An evaluation of precordial ultrasonic monitoring to avoid bends at altitude," *Aviat Space Environ Med*, vol. 59, pp. 635-9, Jul 1988.

[192] U. I. Balldin, A. A. Pilmanis, and J. T. Webb, "Pulmonary decompression sickness at altitude: early symptoms and circulating gas emboli," *Aviation, space, and environmental medicine*, vol. 73, pp. 996-999, 2002.

[193] J. T. Webb and A. A. Pilmanis, "Fifty years of decompression sickness research at Brooks AFB, TX: 1960-2010," *Aviat Space Environ Med*, vol. 82, pp. A1-25, May 2011.

[194] V. K. Kumar, R. D. Billica, and J. M. Waligora, "Utility of Doppler-detectable microbubbles in the diagnosis and treatment of decompression sickness," *Aviat Space Environ Med*, vol. 68, pp. 151-8, Feb 1997.

[195] D. A. Diesel, M. T. Ryles, A. A. Pilmanis, and U. I. Balldin, "Non-invasive measurement of pulmonary artery pressure in humans with simulated altitude-induced venous gas emboli," *Aviat Space Environ Med*, vol. 73, pp. 128-33, Feb 2002.

[196] A. Hadley III, J. Conkin, J. Waligora, and D. Horrigan Jr, "Pulmonary artery location during microgravity activity: potential impact for chest-mounted Doppler during space travel," 1984.

[197] K. Acock, M. Gernhardt, J. Conkin, and M. Powell, "Field Evaluation in Four NEEMO Divers of a Prototype In-suit Doppler Ultrasound Bubble Detector," in *Undersea and 13 Hyperbaric Medical Society Annual Scientific Meeting*, Dallas, TX, 2004.

[198] R. S. Srinivasan, W. A. Gerth, and M. R. Powell, "Mathematical model of diffusion-limited evolution of multiple gas bubbles in tissue," *Ann Biomed Eng*, vol. 31, pp. 471-81, Apr 2003.
---
[199] R. D. Vann, W. A. Gerth, N. E. Leatherman, and M. D. Feezor, "A likelihood analysis of experiments to test altitude decompression protocols for shuttle operations," *Aviat Space Environ Med*, vol. 58, pp. A106-9, Sep 1987.

[200] J. Conkin, "Probabilistic modeling of hypobaric decompression sickness [Dissertation]," Buffalo, NY: State University of New York at Buffalo, 1994.

[201] J. Conkin, K. Kumar, M. Powell, P. Foster, and J. Waligora, "A probabilistic model of hypobaric decompression sickness based on 66 chamber tests," *Aviation, space, and environmental medicine*, vol. 67, pp. 176-183, 1996.

[202] V. Chadov, L. Isseev, and S. Filipenkov, "Assessment of the atmospheric parameters of the space craft and space suit ensuring decompression safety during episodic extra-vehicular activity," *SAE transactions*, pp. 425-434, 1996.

[203] A. S. Barer, "Physiological and medical aspects of the EVA. The Russian experience," SAE Technical Paper 0148-7191, 1995.

[204] P. S. Epstein and M. S. Plesset, "On the stability of gas bubbles in liquid-gas solutions," *The Journal of Chemical Physics*, vol. 18, pp. 1505-1509, 1950.

[205] H. D. Van Liew and M. P. Hlastala, "Influence of bubble size and blood perfusion on absorption of gas bubbles in tissues," *Respir Physiol*, vol. 7, pp. 111-21, Jun 1969.

[206] M. L. Gernhardt, *Development and evaluation of a decompression stress index based on tissue bubble dynamics*: University of Pennsylvania, 1991.

[207] W. Gerth and R. Vann, "Probabilistic gas and bubble dynamics models of decompression sickness occurrence in air and nitrogen-oxygen diving," *Undersea & hyperbaric medicine: journal of the Undersea and Hyperbaric Medical Society, Inc*, vol. 24, pp. 275-292, 1997.

[208] E. D. Thalmann, E. C. Parker, S. S. Survanshi, and P. K. Weathersby, "Improved probabilistic decompression model risk predictions using linear-exponential kinetics," *Undersea Hyperb Med*, vol. 24, pp. 255-74, Winter 1997.

[209] R. S. Srinivasan, W. A. Gerth, and M. R. Powell, "Mathematical model of diffusion-limited gas bubble dynamics in unstirred tissue with finite volume," *Ann Biomed Eng*, vol. 30, pp. 232-46, Feb 2002.

[210] V. Nikolayev, D. Chatain, and D. Beysens, "PHYSICAL MODELLING OF THE BOILING CRISIS: THEORY AND EXPERIMENT Modélisation physique de la crise d'ébullition: théorie et expérience," 2008.

[211] P. P. Foster, A. H. Feiveson, and A. M. Boriek, "Predicting time to decompression illness during exercise at altitude, based on formation and growth of bubbles," *Am J Physiol Regul Integr Comp Physiol*, vol. 279, pp. R2317-28, Dec 2000.

[212] P. P. Foster, A. H. Feiveson, R. Glowinski, M. Izygon, and A. M. Boriek, "A model for influence of exercise on formation and growth of tissue bubbles during altitude decompression," *Am J Physiol Regul Integr Comp Physiol*, vol. 279, pp. R2304-16, Dec 2000.

[213] A. A. Pilmanis, L. J. Petropoulos, N. Kannan, and J. T. Webb, "Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures," *Aviat Space Environ Med*, vol. 75, pp. 749-59, Sep 2004.

[214] P. K. Weathersby and W. A. Gerth, "Survival analysis and maximum likelihood techniques as applied to physiological modeling," in *51st Undersea and Hyperbaric Medical Society Workshop*, Kensington, MD, 2002.
---
[215] M. Gernhardt, "Overview of Shuttle and ISS Exercise Prebreathe Protocols and ISS Protocol Accept/Reject Limits. Prebreathe Protocol for Extravehicular Activity Technical Consultation Report," 2008.

[216] J. J. Freiberger, S. J. Lyman, P. J. Denoble, C. F. Pieper, and R. D. Vann, "Consensus factors used by experts in the diagnosis of decompression illness," *Aviat Space Environ Med*, vol. 75, pp. 1023-8, Dec 2004.

[217] J. R. Norcross, P. Norsk, J. Law, D. Arias, J. Conkin, M. Perchonok, *et al.*, "Effects of the 8 psia/32% O2 atmosphere on the human in the spaceflight environment," vol. NASA/TM-2013-217377, ed. Hanover, MD: National Aeronautics and Space Administration, 2013.

[218] J. Conkin, A. F. Abercromby, J. P. Dervay, A. H. Feiveson, M. L. Gernhardt, J. R. Norcross, *et al.*, "Hypobaric Decompression Sickness Treatment Model," *Aerosp Med Hum Perform*, vol. 86, pp. 508-17, Jun 2015.

[219] J. Conkin, A. Feiveson, M. Gernhardt, J. Norcross, and J. Wessel III, "Designing an Exploration Atmosphere Prebreathe Protocol," in *2015 Human Research Program Investigators''Workshop: Integrated Pathways to Mars*, 2015.

[220] J. Conkin, "Probability of Decompression Sickness and Venous Gas Emboli from 49 NASA Hypobaric Chamber Tests with Reference to Exploration Atmosphere," 2020.

[221] J. P. Dervay, R. W. Sanders, A. Garbino, J. R. Norcross, A. Abercromby, J. Pattarini, *et al.*, "EVALUATION OF DCS TREATMENT CAPABILITIES WHEN PERFORMING EVA FROM REDUCED PRESSURE ENVIRONMENTS," *Aerosp Med Hum Perform*, vol. 93, p. 204, 2022.

[222] J. H. Wessel, 3rd, C. M. Schaefer, M. S. Thompson, J. R. Norcross, and O. S. Bekdash, "Retrospective Evaluation of Clinical Symptoms Due to Mild Hypobaric Hypoxia Exposure in Microgravity," *Aerosp Med Hum Perform*, vol. 89, pp. 792-797, Sep 1 2018.

[223] J. Conkin, J. H. Wessel, 3rd, J. R. Norcross, O. S. Bekdash, A. F. J. Abercromby, M. D. Koslovsky, *et al.*, "Hemoglobin Oxygen Saturation with Mild Hypoxia and Microgravity," *Aerosp Med Hum Perform*, vol. 88, pp. 527-534, Jun 1 2017.

[224] R. A. Scheuring, J. Conkin, J. A. Jones, and M. L. Gernhardt, "Risk assessment of physiological effects of atmospheric composition and pressure in Constellation vehicles," *Acta Astronautica*, pp. 727-739, 2008.

[225] A. B. Montgomery, J. Mills, and J. M. Luce, "Incidence of acute mountain sickness at intermediate altitude," *J. Am. Med. Ass.*, pp. 732-734, 1989.

[226] J. Conkin and J. H. Wessel III, "A model to predict acute mountain sickness in future spacecraft," NASA, Houston, TX, NASA Technical Publication NASA/TP-2009-214791, 2009.

[227] R. C. Roach, D. Maes, D. Sandoval, R. A. Robergs, M. Icenogle, H. Hinghofer-Szalkay, *et al.*, "Exercise exacerbates acute mountain sickness at simulated high altitude," *J. Appl. Physiol.*, vol. 88, pp. 581-5, Frb 2000.

[228] R. C. Roach, J. A. Loeppky, and M. V. Icenogle, "Acute mountain sickness: increased severity during simulated altitude compared with normobaric hypoxia," *J Appl Physiol (1985)*, vol. 81, pp. 1908-10, Nov 1996.

[229] P. Anderson, W. D. Miller, K. A. O'Malley, and M. L. Ceridon, "Incidence and symptoms of high altitude illness in South Pole workers: Antarctic study of altitude physiology," *Clinical medicine Insights: Circulatory, Respiratory and Pulmonary Medicine*, pp. 27-35, 2011.

93
---
[230] J. Conkin and J. H. Wessel III, "Critique of the equivalent air altitude model," *Aviat Space Environ Med*, vol. 79, pp. 975-982, 2008.

[231] E. A. W. G. NASA, "Recommendations for exploration spacecraft internal atmospheres: The final report of the NASA exploration atmospheres working group. NASA Technical Publication NASA/TP-2010-216134," 2010.

[232] S. C. Walker, A. Garbino, K. Ray, R. Hardwick, D. T. Fitzpatrick, and R. W. Sanders, "Oxygen exposures at NASA's Neutral Buoyancy Lab: a 20-year experience," *Undersea Hyperb Med*, vol. 45, pp. 427-436, Jul-Aug 2018.

[233] J. P. Dervay, "Spaceflight Decompression Sickness Contingency Plan," 2007.

[234] NASA, "Human Landing System (HLS) Requirements Document," ed. George C. Marshall Space Flight Center, Alabama, 35812, 2019.

[235] H. Kunz, H. Quiriarte, R. J. Simpson, R. Ploutz-Snyder, K. McMonigal, C. Sams, *et al.*, "Alterations in hematologic indices during long-duration spaceflight," *BMC Hematol*, vol. 17, p. 12, 2017.

[236] S. Gallagher and P. Hackett. (2022, April 26, 2023). *Patient education: High-altitude illness (including mountain sickness) (Beyond the Basics)*. Available: https://www.uptodate.com/contents/high-altitude-illness-including-mountain-sickness-beyond-the-basics

[237] W. O. Fenn, H. Rahn, and A. B. Otis, "A theoretical study of the composition of the alveolar air at altitude," *Amer. J. Physiol.*, vol. 146, pp. 637-653, 1946.

[238] H. Rahn and W. O. Fenn, "A graphical analysis of the respiratory gas exchange: the O2 - CO2 diagram.," ed Washington, DC: The American Physiological Society, 1956, pp. 2nd ed. p25-26.

[239] A. F. Abercromby, O. Bekdash, J. S. Cupples, J. T. Dunn, L. T. Dillion, A. Garbino, *et al.*, "Crew Health and Performance Extravehicular Activity Roadmap: 2020," ed, 2020.