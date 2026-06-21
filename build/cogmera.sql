--
-- PostgreSQL database dump
--

\restrict iXxcaa4uDWeb91ErsRBKAivG2AnaCoibkJZCr51LbBzsf3wD7roMlSzlhgd2Fax

-- Dumped from database version 17.10 (Debian 17.10-1.pgdg13+1)
-- Dumped by pg_dump version 17.10 (Debian 17.10-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: countries; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.countries (
    country_id bigint NOT NULL,
    country text
);


ALTER TABLE public.countries OWNER TO stringwave;

--
-- Name: countries_country_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.countries_country_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.countries_country_id_seq OWNER TO stringwave;

--
-- Name: countries_country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.countries_country_id_seq OWNED BY public.countries.country_id;


--
-- Name: decades; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.decades (
    decade_id bigint NOT NULL,
    decade bigint
);


ALTER TABLE public.decades OWNER TO stringwave;

--
-- Name: decades_decade_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.decades_decade_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.decades_decade_id_seq OWNER TO stringwave;

--
-- Name: decades_decade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.decades_decade_id_seq OWNED BY public.decades.decade_id;


--
-- Name: genres; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.genres (
    genre_id bigint NOT NULL,
    genre text
);


ALTER TABLE public.genres OWNER TO stringwave;

--
-- Name: genres_genre_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.genres_genre_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genres_genre_id_seq OWNER TO stringwave;

--
-- Name: genres_genre_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.genres_genre_id_seq OWNED BY public.genres.genre_id;


--
-- Name: sort_methods; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.sort_methods (
    sort_method_id bigint NOT NULL,
    sort_method text
);


ALTER TABLE public.sort_methods OWNER TO stringwave;

--
-- Name: sort_methods_sort_method_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.sort_methods_sort_method_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sort_methods_sort_method_id_seq OWNER TO stringwave;

--
-- Name: sort_methods_sort_method_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.sort_methods_sort_method_id_seq OWNED BY public.sort_methods.sort_method_id;


--
-- Name: styles; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.styles (
    style_id bigint NOT NULL,
    style text
);


ALTER TABLE public.styles OWNER TO stringwave;

--
-- Name: styles_style_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.styles_style_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.styles_style_id_seq OWNER TO stringwave;

--
-- Name: styles_style_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.styles_style_id_seq OWNED BY public.styles.style_id;


--
-- Name: years; Type: TABLE; Schema: public; Owner: stringwave
--

CREATE TABLE public.years (
    year_id bigint NOT NULL,
    year text
);


ALTER TABLE public.years OWNER TO stringwave;

--
-- Name: years_year_id_seq; Type: SEQUENCE; Schema: public; Owner: stringwave
--

CREATE SEQUENCE public.years_year_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.years_year_id_seq OWNER TO stringwave;

--
-- Name: years_year_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: stringwave
--

ALTER SEQUENCE public.years_year_id_seq OWNED BY public.years.year_id;


--
-- Name: countries country_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.countries ALTER COLUMN country_id SET DEFAULT nextval('public.countries_country_id_seq'::regclass);


--
-- Name: decades decade_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.decades ALTER COLUMN decade_id SET DEFAULT nextval('public.decades_decade_id_seq'::regclass);


--
-- Name: genres genre_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.genres ALTER COLUMN genre_id SET DEFAULT nextval('public.genres_genre_id_seq'::regclass);


--
-- Name: sort_methods sort_method_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.sort_methods ALTER COLUMN sort_method_id SET DEFAULT nextval('public.sort_methods_sort_method_id_seq'::regclass);


--
-- Name: styles style_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.styles ALTER COLUMN style_id SET DEFAULT nextval('public.styles_style_id_seq'::regclass);


--
-- Name: years year_id; Type: DEFAULT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.years ALTER COLUMN year_id SET DEFAULT nextval('public.years_year_id_seq'::regclass);


--
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.countries (country_id, country) FROM stdin;
1	US
2	UK
3	Germany
4	France
5	Japan
6	Italy
7	Europe
8	Canada
9	Netherlands
10	Unknown
11	Spain
12	Australia
13	Russia
14	Sweden
15	Brazil
16	Belgium
17	Greece
18	Poland
19	Mexico
20	Jamaica
21	Finland
22	Switzerland
23	USSR
24	Denmark
25	Argentina
26	Portugal
27	Norway
28	Austria
29	UK & Europe
30	New Zealand
31	South Africa
32	Yugoslavia
33	Hungary
34	Colombia
35	USA & Canada
36	Ukraine
37	Turkey
38	India
39	Czech Republic
40	Czechoslovakia
41	Venezuela
42	Ireland
43	Romania
44	Indonesia
45	Taiwan
46	Chile
47	Peru
48	South Korea
49	Israel
50	Worldwide
51	Bulgaria
52	Thailand
53	Malaysia
54	Scandinavia
55	German Democratic Republic (GDR)
56	China
57	Croatia
58	Hong Kong
59	Philippines
60	Serbia
61	Ecuador
62	UK, Europe & US
63	Lithuania
64	Germany, Austria, & Switzerland
65	USA & Europe
66	Singapore
67	Slovakia
68	Uruguay
69	Slovenia
70	Australasia
71	Australia & New Zealand
72	Iceland
73	Bolivia
74	UK & Ireland
75	Nigeria
76	Benelux
77	USA, Canada & Europe
78	Estonia
79	Panama
80	UK & US
81	Pakistan
82	Lebanon
83	Egypt
84	Cuba
85	Costa Rica
86	Middle East
87	Latvia
88	Puerto Rico
89	Kenya
90	Iran
91	Belarus
92	Guatemala
93	Morocco
94	Saudi Arabia
95	Trinidad & Tobago
96	Barbados
97	USA, Canada & UK
98	Luxembourg
99	Bosnia & Herzegovina
100	Macedonia
101	Czech Republic & Slovakia
102	Madagascar
103	Ghana
104	Zimbabwe
105	El Salvador
106	North America (inc Mexico)
107	Singapore, Malaysia & Hong Kong
108	Algeria
109	Dominican Republic
110	France & Benelux
111	Ivory Coast
112	Tunisia
113	Reunion
114	Serbia and Montenegro
115	Angola
116	Zaire
117	Georgia
118	United Arab Emirates
119	Germany & Switzerland
120	Congo, Democratic Republic of the
121	Malta
122	Mozambique
123	Rhodesia
124	Asia
125	Cyprus
126	Mauritius
127	Azerbaijan
128	Zambia
129	Nicaragua
130	Kazakhstan
131	Syria
132	Paraguay
133	Senegal
134	Guadeloupe
135	UK & France
136	Vietnam
137	UK, Europe & Japan
138	Bahamas, The
139	Ethiopia
140	Suriname
141	Haiti
142	Singapore & Malaysia
143	Albania
144	Faroe Islands
145	Moldova, Republic of
146	South East Asia
147	Cameroon
148	Gulf Cooperation Council
149	South Vietnam
150	South America
151	Uzbekistan
152	Honduras
153	Martinique
154	Benin
155	Kuwait
156	Sri Lanka
157	Andorra
158	Netherlands Antilles
159	Liechtenstein
160	Dahomey
161	Mali
162	Burma
163	Guinea
164	Congo, Republic of the
165	Sudan
166	Kosovo
167	Mongolia
168	Nepal
169	French Polynesia
170	Greenland
171	Virgin Islands
172	Southern Rhodesia
173	Uganda
174	Bangladesh
175	Dutch East Indies
176	North Korea
177	Armenia
178	Cape Verde
179	Bermuda
180	Iraq
181	Central America
182	Seychelles
183	Cambodia
184	Guyana
185	Tanzania
186	Bahrain
187	Jordan
188	Libya
189	Antigua & Barbuda
190	Montenegro
191	Gabon
192	Palestine
193	Man, Isle of
194	Belgian Congo
195	Togo
196	Afghanistan
197	Yemen
198	Monaco
199	Papua New Guinea
200	Cayman Islands
201	Belize
202	Fiji
203	New Caledonia
204	Upper Volta
205	UK & Germany
206	Austria-Hungary
207	East Timor
208	Singapore, Malaysia, Hong Kong & Thailand
209	Laos
210	French Guiana
211	Aruba
212	Dominica
213	Africa
214	San Marino
215	Kyrgyzstan
216	Burkina Faso
217	UK, Europe & Israel
218	Turkmenistan
219	Sierra Leone
220	Brunei
221	Namibia
222	Marshall Islands
223	North & South America
224	Eritrea
225	Saint Kitts and Nevis
226	Botswana
227	Ottoman Empire
228	Guernsey
229	Jersey
230	Central African Republic
231	Guam
232	Grenada
233	Qatar
234	Somalia
235	Liberia
236	Macau
237	Sint Maarten
238	Saint Lucia
239	Lesotho
240	Niger
241	Maldives
242	Bhutan
243	Protectorate of Bohemia and Moravia
244	Saint Vincent and the Grenadines
245	Malawi
246	Micronesia, Federated States of
247	Gambia, The
248	Guinea-Bissau
249	Indochina
250	Comoros
251	Gibraltar
252	Palau
253	Korea (pre-1945)
254	Mauritania
255	Vatican City
256	Cook Islands
257	Tajikistan
258	Bohemia
259	Rwanda
260	Samoa
261	Oman
262	Anguilla
263	South Pacific
264	Abkhazia
265	British Virgin Islands
266	Hong Kong & Thailand
267	Antigua & Barbuda
268	Djibouti
269	Montserrat
270	Sao Tome and Principe
271	Vanuatu
272	Mayotte
273	Tonga
274	South West Africa
275	Swaziland
276	West Bank
277	Norfolk Island
278	Turks and Caicos Islands
279	Northern Mariana Islands
280	Solomon Islands
281	Equatorial Guinea
282	Southern Sudan
283	American Samoa
284	Chad
285	Falkland Islands
286	Gaza Strip
287	Pitcairn Islands
288	Zanzibar
289	Antarctica
290	Korea
291	Nauru
292	Niue
293	Saint Pierre and Miquelon
294	Tokelau
295	Tuvalu
296	Wallis and Futuna
\.


--
-- Data for Name: decades; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.decades (decade_id, decade) FROM stdin;
1	2020
2	2010
3	2000
4	1990
5	1980
6	1970
7	1960
8	1950
9	1940
10	1930
11	1920
12	1910
13	1900
14	1890
\.


--
-- Data for Name: genres; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.genres (genre_id, genre) FROM stdin;
1	Rock
2	Electronic
3	Pop
4	Folk, World, & Country
5	Jazz
6	Funk/Soul
7	Classical
8	Hip Hop
9	Latin
10	Stage & Screen
11	Reggae
12	Blues
13	Non-Music
14	Children's
15	Brass & Military
\.


--
-- Data for Name: sort_methods; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.sort_methods (sort_method_id, sort_method) FROM stdin;
1	date_added
2	date_changed
3	title
4	want
5	have
6	hot
\.


--
-- Data for Name: styles; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.styles (style_id, style) FROM stdin;
1	Pop Rock
2	House
3	Vocal
4	Experimental
5	Punk
6	Synth-pop
7	Alternative Rock
8	Techno
9	Soul
10	Disco
11	Indie Rock
12	Ambient
13	Hardcore
14	Folk
15	Country
16	Hard Rock
17	Ballad
18	Electro
19	Rock & Roll
20	Chanson
21	Trance
22	Heavy Metal
23	Psychedelic Rock
24	Folk Rock
25	Downtempo
26	Romantic
27	Soundtrack
28	Classic Rock
29	Noise
30	Schlager
31	Prog Rock
32	Funk
33	Easy Listening
34	Black Metal
35	Tech House
36	Blues Rock
37	New Wave
38	Rhythm & Blues
39	Deep House
40	Industrial
41	Death Metal
42	Classical
43	Euro House
44	Drum n Bass
45	Progressive House
46	Soft Rock
47	Abstract
48	Garage Rock
49	Minimal
50	Europop
51	Gospel
52	Acoustic
53	Thrash
54	Baroque
55	Swing
56	Big Band
57	Modern
58	Dub
59	Country Rock
60	Breakbeat
61	Contemporary Jazz
62	RnB/Swing
63	Drone
64	Progressive Trance
65	Indie Pop
66	Dancehall
67	Opera
68	IDM
69	Breaks
70	Contemporary
71	Reggae
72	African
73	Art Rock
74	Fusion
75	Dark Ambient
76	Gangsta
77	Doom Metal
78	Avantgarde
79	Hard Trance
80	Post-Punk
81	Pop Rap
82	Religious
83	Rockabilly
84	Beat
85	Roots Reggae
86	Electro House
87	Acid
88	Jazz-Funk
89	Lo-Fi
90	Instrumental
91	Dance-pop
92	Comedy
93	Score
94	Grindcore
95	Leftfield
96	Ska
97	Dubstep
98	Theme
99	Soul-Jazz
100	Post Rock
101	Power Pop
102	Hip Hop
103	Psy-Trance
104	Spoken Word
105	Glam
106	Modern Classical
107	Bop
108	Goth Rock
109	Salsa
110	New Age
111	Hard House
112	Jazz-Rock
113	Conscious
114	Bolero
115	Free Improvisation
116	Trip Hop
117	Latin Jazz
118	Musical
119	Italo-Disco
120	Contemporary R&B
121	Emo
122	Cumbia
123	Stoner Rock
124	EBM
125	Hard Bop
126	Shoegaze
127	J-pop
128	Surf
129	MPB
130	Free Jazz
131	Garage House
132	Doo Wop
133	Jungle
134	Field Recording
135	Oi
136	Volksmusik
137	Story
138	Cool Jazz
139	Samba
140	Hardstyle
141	Happy Hardcore
142	Post Bop
143	UK Garage
144	Tango
145	Pop Punk
146	Bluegrass
147	Tribal
148	Synthwave
149	Celtic
150	Radioplay
151	Darkwave
152	Eurodance
153	Novelty
154	Smooth Jazz
155	Vaporwave
156	Italodance
157	Flamenco
158	Polka
159	Grunge
160	Dixieland
161	Arena Rock
162	Metalcore
163	Future Jazz
164	Symphonic Rock
165	Southern Rock
166	Hardcore Hip-Hop
167	Choral
168	Latin
169	Parody
170	AOR
171	Progressive Metal
172	Nu Metal
173	Hindustani
174	Glitch
175	Trap
176	Rumba
177	Gabber
178	Space Rock
179	Krautrock
180	Cha-Cha
181	Dub Techno
182	Hi NRG
183	Thug Rap
184	Speed Metal
185	Bossa Nova
186	Merengue
187	Power Metal
188	Audiobook
189	Breakcore
190	Bollywood
191	Reggae-Pop
192	Acid House
193	Poetry
194	Boom Bap
195	Power Electronics
196	Neo-Classical
197	Harsh Noise Wall
198	Avant-garde Jazz
199	Mod
200	Boogie
201	Electric Blues
202	Jazzy Hip-Hop
203	Freestyle
204	Renaissance
205	Acid Jazz
206	Bossanova
207	Mambo
208	Country Blues
209	Chiptune
210	Marches
211	Post-Hardcore
212	Big Beat
213	Tribal House
214	Sludge Metal
215	Interview
216	Ranchera
217	Dungeon Synth
218	Math Rock
219	Bass Music
220	Broken Beat
221	Calypso
222	Modal
223	Chicago Blues
224	Rocksteady
225	Minimal Techno
226	Neofolk
227	Ethereal
228	Psychedelic
229	Education
230	Nu-Disco
231	Indian Classical
232	Afrobeat
233	Berlin-School
234	Light Music
235	Lounge
236	Afro-Cuban
237	Neo Soul
238	Grime
239	Crust
240	Goa Trance
241	Hip-House
242	Impressionist
243	Ragtime
244	Lovers Rock
245	Guaracha
246	Operetta
247	G-Funk
248	Britpop
249	Mandopop
250	Rhythmic Noise
251	Euro-Disco
252	Gothic Metal
253	Chillwave
254	Psychobilly
255	Brass Band
256	Nursery Rhymes
257	Neo-Romantic
258	Cut-up/DJ
259	Medieval
260	Pacific
261	Melodic Death Metal
262	Tech Trance
263	Ragga
264	Dialogue
265	Canzone Napoletana
266	Symphonic Metal
267	Son
268	Speedcore
269	Deep Techno
270	Ragga HipHop
271	Twist
272	Goregrind
273	Space-Age
274	Video Game Music
275	Honky Tonk
276	Promotional
277	Fado
278	Eurobeat
279	Nordic
280	Educational
281	Political
282	Military
283	Funk Metal
284	Music Hall
285	Melodic Hardcore
286	Highlife
287	Acid Rock
288	Hard Techno
289	Dream Pop
290	Makina
291	Soca
292	Soukous
293	Atmospheric Black Metal
294	Afro-Cuban Jazz
295	Jazzdance
296	New Jack Swing
297	Mariachi
298	Zouk
299	Speech
300	Folk Metal
301	Monolog
302	Sound Collage
303	Deathcore
304	Piano Blues
305	Hawaiian
306	Delta Blues
307	K-pop
308	Horrorcore
309	Reggaeton
310	Romani
311	Modern Electric Blues
312	Freetekno
313	Witch House
314	New Beat
315	Cubano
316	Noisecore
317	Hands Up
318	Viking Metal
319	Gypsy Jazz
320	Luk Thung
321	Public Broadcast
322	Bubblegum
323	Post-Metal
324	Jumpstyle
325	Coldwave
326	City Pop
327	Italo House
328	Texas Blues
329	Harmonica Blues
330	Boogaloo
331	No Wave
332	Speed Garage
333	Special Effects
334	Cajun
335	Therapy
336	J-Rock
337	Post-Modern
338	Sound Art
339	Vallenato
340	Bhangra
341	Pub Rock
342	P.Funk
343	Oratorio
344	Jump Blues
345	Enka
346	Illbient
347	Corrido
348	Porro
349	Bassline
350	Electroacoustic
351	Descarga
352	Hillbilly
353	Pachanga
354	Rebetiko
355	Holiday
356	Louisiana Blues
357	Tejano
358	Guajira
359	Boogie Woogie
360	Beguine
361	Screw
362	Donk
363	Son Montuno
364	Karaoke
365	Depressive Black Metal
366	Deathrock
367	Nueva Cancion
368	Juke
369	Industrial Metal
370	Charanga
371	Cloud Rap
372	Power Violence
373	Technical Death Metal
374	Klezmer
375	Copla
376	Chinese Classical
377	Western Swing
378	Sermon
379	Crunk
380	Technical
381	Andean Music
382	Groove Metal
383	Compas
384	Cantopop
385	DJ Battle Tool
386	Aboriginal
387	Ghetto
388	Brit Pop
389	Disco Polo
390	Swingbeat
391	Tropical House
392	Pasodoble
393	Electroclash
394	Danzon
395	Bounce
396	Bachata
397	Free Funk
398	Health-Fitness
399	Funeral Doom Metal
400	Minneapolis Sound
401	Bayou Funk
402	Batucada
403	Zydeco
404	Appalachian Music
405	Turntablism
406	Conjunto
407	Jangle Pop
408	Catalan Music
409	Levenslied
410	Halftime
411	Carnatic
412	Pornogrind
413	Sea Shanties
414	Quechua
415	Movie Effects
416	Steel Band
417	Progressive Breaks
418	Hokkien Pop
419	Skiffle
420	Lambada
421	Swamp Pop
422	Liscio
423	Ethno-pop
424	Early
425	Ghetto House
426	J-Core
427	Pipe & Drum
428	Sound Poetry
429	Doomcore
430	Footwork
431	Miami Bass
432	Cretan
433	Bleep
434	Gamelan
435	Indo-Pop
436	Plena
437	Horror Rock
438	Choro
439	Schranz
440	Musette
441	Ottoman Classical
442	Mizrahi
443	Kwaito
444	Nueva Trova
445	Persian Classical
446	Erotic
447	Glitch Hop
448	Britcore
449	Zarzuela
450	Trova
451	Ghazal
452	Barbershop
453	Zamba
454	Basque Music
455	Huayno
456	Group Sounds
457	Public Service Announcement
458	UK Street Soul
459	NDW
460	Bengali Music
461	Chacarera
462	Dangdut
463	Go-Go
464	Memphis Blues
465	East Coast Blues
466	Beatdown
467	Neo Trance
468	Luk Krung
469	Tamil Film Music
470	Ghettotech
471	Twelve-tone
472	Chutney
473	Reggae Gospel
474	Gaita
475	Kaseko
476	Joropo
477	Mo Lam
478	Cabaret
479	Qawwali
480	K-Rock
481	Balearic
482	Hyphy
483	Dub Poetry
484	Marimba
485	Rock Opera
486	Timba
487	Hiplife
488	Keroncong
489	Morna
490	UK Funky
491	Piedmont Blues
492	Gogo
493	Cape Jazz
494	Guarania
495	Favela Funk
496	Andalusian Classical
497	Mento
498	Medical
499	Baltimore Club
500	Overtone Singing
501	Jibaro
502	Sephardic
503	Jota
504	Hyperpop
505	Phleng Phuea Chiwit
506	Maloya
507	Phonk
508	Salegy
509	Spirituals
510	Sertanejo
511	Baroque Pop
512	Griot
513	Dark Jazz
514	Hard Beat
515	Lento Violento
516	Marcha Carnavalesca
517	Villancicos
518	Izvorna
519	Beatbox
520	Thai Classical
521	Serial
522	Mbalax
523	Bomba
524	Mugham
525	Candombe
526	Gagaku
527	Galician Traditional
528	Skweee
529	Nerdcore Techno
530	Vaudeville
531	Cuatro
532	Stride
533	Ballroom
534	Shaabi
535	Electro Swing
536	Gusle
537	Caipira
538	Aguinaldo
539	Champeta
540	Sonero
541	Kizomba
542	Organ
543	Zemer Ivri
544	Kolo
545	Jug Band
546	Break-In
547	Seresta
548	Jersey Club
549	Yemenite Jewish
550	Philippine Classical
551	Funkot
552	Gwo Ka
553	Milonga
554	Junkanoo
555	Mouth Music
556	Bambuco
557	Rune Singing
558	Occitan
559	Cobla
560	Moombahton
561	Piobaireachd
562	Hill Country Blues
563	Taarab
564	Anison
565	Filk
566	Korean Court Music
567	Progressive Bluegrass
568	Waiata
569	Comfy Synth
570	Rapso
571	Bubbling
572	Cantorial
573	Low Bap
574	Exotica
575	Cambodian Classical
576	Bangladeshi Classical
577	Lao Music
578	Bitpop
579	Guggenmusik
580	Klasik
581	Gqom
582	Kuduro
583	Sunshine Pop
584	Bongo Flava
585	Drill
586	Hardcore Punk
587	Motswako
588	French House
589	Future Bass
590	Alt-Pop
591	Spaza
592	Frevo
593	Shidaiqu
594	Hyper Techno
595	Azonto
596	Future Pop
597	Alternative Metal
598	Russian Pop
599	Zhongguo Feng
600	Noise Rock
601	Plunderphonics
602	V-pop
603	Unblack Metal
604	Currulao
605	Lowercase
606	Trallalero
607	Neopagan
608	Microhouse
609	Dark Electro
610	Latin Pop
611	Ambient House
612	Slowcore
613	Amapiano
614	Blackgaze
615	Future House
616	Mathcore
617	Nintendocore
618	Shoegazer
619	Banda
620	Crossover thrash
621	Hypnagogic pop
622	Occult
623	Ballet
624	Honkyoku
625	Jiuta
626	Post-Grunge
627	Shinkyoku
628	Singeli
629	Sokyoku
630	Bakersfield Sound
631	Geet
632	Sankyoku
633	Shomyo
\.


--
-- Data for Name: years; Type: TABLE DATA; Schema: public; Owner: stringwave
--

COPY public.years (year_id, year) FROM stdin;
1	2023
2	2022
3	2021
4	2018
5	2017
6	2016
7	2015
8	2014
9	2013
10	2012
11	2011
12	2008
13	2007
14	2006
15	2005
16	2004
17	2003
18	2002
19	2001
20	1998
21	1997
22	1996
23	1995
24	1994
25	1993
26	1992
27	1991
28	1988
29	1987
30	1986
31	1985
32	1984
33	1983
34	1982
35	1981
36	1978
37	1977
38	1976
39	1975
40	1974
41	1973
42	1972
43	1971
44	1968
45	1967
46	1966
47	1965
48	1964
49	1963
50	1962
51	1961
52	1958
53	1957
54	1956
55	1955
56	1954
57	1953
58	1952
59	1951
60	1948
61	1947
62	1946
63	1945
64	1944
65	1943
66	1942
67	1941
68	1938
69	1937
70	1936
71	1935
72	1934
73	1933
74	1932
75	1931
76	1928
77	1927
78	1926
79	1925
80	1924
81	1923
82	1922
83	1921
84	1918
85	1917
86	1916
87	1915
88	1914
89	1913
90	1912
91	1911
92	1908
93	1907
94	1906
95	1905
96	1904
97	1903
98	1902
99	1901
100	1898
101	1897
102	1896
103	1895
104	1894
105	1893
106	1892
107	1891
\.


--
-- Name: countries_country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.countries_country_id_seq', 296, true);


--
-- Name: decades_decade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.decades_decade_id_seq', 14, true);


--
-- Name: genres_genre_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.genres_genre_id_seq', 15, true);


--
-- Name: sort_methods_sort_method_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.sort_methods_sort_method_id_seq', 6, true);


--
-- Name: styles_style_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.styles_style_id_seq', 633, true);


--
-- Name: years_year_id_seq; Type: SEQUENCE SET; Schema: public; Owner: stringwave
--

SELECT pg_catalog.setval('public.years_year_id_seq', 107, true);


--
-- Name: styles idx_16470_styles_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.styles
    ADD CONSTRAINT idx_16470_styles_pkey PRIMARY KEY (style_id);


--
-- Name: genres idx_16477_genres_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT idx_16477_genres_pkey PRIMARY KEY (genre_id);


--
-- Name: decades idx_16484_decades_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.decades
    ADD CONSTRAINT idx_16484_decades_pkey PRIMARY KEY (decade_id);


--
-- Name: countries idx_16489_countries_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT idx_16489_countries_pkey PRIMARY KEY (country_id);


--
-- Name: years idx_16496_years_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.years
    ADD CONSTRAINT idx_16496_years_pkey PRIMARY KEY (year_id);


--
-- Name: sort_methods idx_16503_sort_methods_pkey; Type: CONSTRAINT; Schema: public; Owner: stringwave
--

ALTER TABLE ONLY public.sort_methods
    ADD CONSTRAINT idx_16503_sort_methods_pkey PRIMARY KEY (sort_method_id);


--
-- PostgreSQL database dump complete
--

\unrestrict iXxcaa4uDWeb91ErsRBKAivG2AnaCoibkJZCr51LbBzsf3wD7roMlSzlhgd2Fax

