/* Le Cahier — le récit : l'histoire elle-même.
   Une page par jour. Chaque page est une scène (récit et dialogue), un seul
   choix de réplique pour comprendre, et trois phrases à trous qui entrent dans
   le planning de révision une fois la page lue : l'histoire nourrit les cartes,
   et ce sont les cartes qui ouvrent la page suivante.

   Format d'une ligne :  {w:"E", fr:"…", en:"…"}   w = qui parle (voir CAST)
   Un choix :            {w:"?", c:[[fr, en, 1], [fr, en, 0], …]}  — 1 = juste
                         (si toutes les réponses sont justes, c'est un choix libre)
   {nom} = le prénom du héros.
   Ce fichier peut être réécrit par le moteur hebdomadaire sans toucher à recit.js. */

const CAST = {
  N:{name:"", face:""},
  E:{name:"Maître Encrier", face:"🧙"},
  M:{name:"Margaux", face:"👩‍🍳"},
  T:{name:"Théo", face:"🚴"},
  B:{name:"La Brume", face:"🌫️"},
  V:{name:"M. Perdu", face:"🧳"},
  C:{name:"Le chef de gare", face:"🧑‍✈️"}
};

const RECIT = {
  titre:"Le Cahier d'Encre",
  titreEn:"The Inkwell Notebook",

  actes:[
    {n:1, lv:2, fr:"Les mots s'effacent", en:"The words are fading",
     fin:"Les mots ont tenu. Mais la Brume n'est pas vaincue : elle t'attend à la gare.",
     finEn:"The words held. But the Mist is not beaten: it is waiting for you at the station."},
    {n:2, lv:2, fr:"Les noms perdus", en:"The lost names",
     fin:"À la gare, les noms sont revenus. La Brume recule vers la vieille bibliothèque, de l'autre côté de l'eau.",
     finEn:"At the station, the names have come back. The Mist retreats to the old library on the other side of the water."}
  ],

  chapitres:[
    {n:0, acte:1, face:"🏘️", fr:"L'arrivée", en:"The arrival"},
    {n:1, acte:1, face:"🥖", fr:"La boulangerie de Margaux", en:"Margaux's bakery"},
    {n:2, acte:1, face:"📮", fr:"Le facteur en retard", en:"The late postman"},
    {n:3, acte:2, face:"🚂", fr:"Le train de huit heures dix", en:"The 8:10 train"},
    {n:4, acte:2, face:"🕰️", fr:"La gare sans nom", en:"The nameless station"}
  ],

  /* Ce que le feuilleton des Chroniques doit savoir pour continuer la même histoire. */
  bible:{
    world:"Le village de Plume-sur-Encre, où une Brume mystérieuse efface les mots que les gens oublient. Chaque mot dont on se souvient fait reculer la Brume.",
    cast:"Maître Encrier (vieux scribe, le guide), Margaux (la boulangère), Théo (le jeune facteur toujours en retard), M. Perdu (un voyageur distrait qui avait oublié son nom), le chef de gare de Montluisant, la Brume (la force qui efface les mots).",
    next:"L'acte III se passe dans la vieille bibliothèque de l'autre côté de la rivière, où la Brume s'est réfugiée : le héros y cherche le premier mot du Cahier, celui qui fait tenir tous les autres."
  },

  pages:[
    {id:"p00", ch:0, lv:2, titre:"La porte verte", titreEn:"The green door",
     lieu:"Plume-sur-Encre · le soir", lieuEn:"Plume-sur-Encre · evening",
     lines:[
       {w:"N", fr:"Le soir tombe sur le village de Plume-sur-Encre.", en:"Evening falls on the village of Plume-sur-Encre."},
       {w:"N", fr:"Tu arrives avec un petit sac et une lettre dans la main.", en:"You arrive with a small bag and a letter in your hand."},
       {w:"N", fr:"Devant une grande porte verte, un vieil homme t'attend avec une lampe.", en:"In front of a big green door, an old man is waiting for you with a lamp."},
       {w:"E", fr:"Bonsoir ! Je m'appelle Maître Encrier. Tu es le nouvel apprenti ?", en:"Good evening! My name is Master Inkwell. Are you the new apprentice?"},
       {w:"?", c:[
         ["Oui, c'est moi. J'ai une lettre pour vous.", "Yes, it's me. I have a letter for you.", 1],
         ["Non, je cherche la gare.", "No, I'm looking for the train station.", 0],
         ["Merci, je n'ai pas faim.", "Thanks, I'm not hungry.", 0]]},
       {w:"E", fr:"Parfait ! Entre vite, il fait froid ce soir.", en:"Perfect! Come in quickly, it's cold tonight."},
       {w:"N", fr:"Dans l'atelier, il y a un grand livre sur la table. C'est le Cahier du village.", en:"In the workshop, there is a big book on the table. It's the village Notebook."},
       {w:"E", fr:"Regarde cette page. Hier, il y avait un mot ici. Aujourd'hui, il n'y a plus rien.", en:"Look at this page. Yesterday, there was a word here. Today, there is nothing left."},
       {w:"E", fr:"C'est la Brume. Elle prend les mots que les gens oublient.", en:"It's the Mist. It takes the words that people forget."},
       {w:"E", fr:"Mais quand on se souvient d'un mot, la Brume recule. Tu vas m'aider, {nom} ?", en:"But when we remember a word, the Mist pulls back. Will you help me, {nom}?"},
       {w:"?", c:[
         ["Oui, avec plaisir !", "Yes, with pleasure!", 1],
         ["Oui, mais j'ai un peu peur.", "Yes, but I'm a little afraid.", 1],
         ["Je vais essayer.", "I'll try.", 1]]},
       {w:"E", fr:"Merci. Alors, commençons demain matin. Dors bien, {nom}.", en:"Thank you. Then let's begin tomorrow morning. Sleep well, {nom}."}
     ],
     cards:[
       {s:"Tu ___ le nouvel apprenti ?", a:"es", d:["est","suis","as"], g:"Are you the new apprentice?"},
       {s:"Dans l'atelier, il y ___ un grand livre sur la table.", a:"a", d:["est","fait","va"], g:"In the workshop, there is a big book on the table."},
       {s:"Hier, il y ___ un mot ici. Aujourd'hui, il n'y a plus rien.", a:"avait", d:["aura","ont","sont"], g:"Yesterday, there was a word here. Today, there is nothing left."}
     ],
     hook:"Demain, tu rencontres Margaux, la boulangère. Elle a perdu quelque chose…", hookEn:"Tomorrow, you meet Margaux, the baker. She has lost something…",
     resume:"{nom} est arrivé à Plume-sur-Encre, où Maître Encrier lui a montré le Cahier du village et expliqué que la Brume efface les mots oubliés."},

    {id:"p01", ch:1, lv:2, titre:"Le premier pain", titreEn:"The first loaf",
     lieu:"La boulangerie · le matin", lieuEn:"The bakery · morning",
     lines:[
       {w:"N", fr:"Le matin, le village sent le pain chaud.", en:"In the morning, the village smells of warm bread."},
       {w:"E", fr:"{nom}, va à la boulangerie. Achète une baguette pour le petit déjeuner.", en:"{nom}, go to the bakery. Buy a baguette for breakfast."},
       {w:"N", fr:"Tu pousses la porte. Une femme sourit derrière le comptoir.", en:"You push the door. A woman smiles behind the counter."},
       {w:"M", fr:"Bonjour ! Je suis Margaux. Qu'est-ce que je vous sers ?", en:"Hello! I'm Margaux. What can I get you?"},
       {w:"?", c:[
         ["Je voudrais une baguette, s'il vous plaît.", "I would like a baguette, please.", 1],
         ["Je cherche la gare, s'il vous plaît.", "I'm looking for the train station, please.", 0],
         ["Je suis très fatigué, merci.", "I'm very tired, thanks.", 0]]},
       {w:"M", fr:"Voilà ! Ça fait un euro vingt.", en:"Here you are! That's one euro twenty."},
       {w:"N", fr:"Tu paies. Puis tu regardes le panneau au-dessus de la porte : BOLANGERIE. Il manque une lettre !", en:"You pay. Then you look at the sign above the door: BOLANGERIE. A letter is missing!"},
       {w:"M", fr:"Ce n'est pas la première fois. La Brume passe chaque nuit.", en:"It's not the first time. The Mist comes by every night."},
       {w:"M", fr:"Reviens demain, {nom}. J'ai besoin d'aide pour ma recette.", en:"Come back tomorrow, {nom}. I need help with my recipe."}
     ],
     cards:[
       {s:"Je ___ une baguette, s'il vous plaît.", a:"voudrais", d:["voulu","vouloir","voudront"], g:"I would like a baguette, please."},
       {s:"Qu'est-ce que je vous ___ ?", a:"sers", d:["serre","sert","servi"], g:"What can I get you?"},
       {s:"J'ai ___ d'aide pour ma recette.", a:"besoin", d:["peur","faim","chaud"], g:"I need help with my recipe."}
     ],
     hook:"Margaux a oublié un mot très important de sa recette…", hookEn:"Margaux has forgotten a very important word from her recipe…",
     resume:"{nom} a acheté une baguette chez Margaux, dont le panneau perd ses lettres à cause de la Brume."},

    {id:"p02", ch:1, lv:2, titre:"La recette perdue", titreEn:"The lost recipe",
     lieu:"La boulangerie · le lendemain", lieuEn:"The bakery · the next day",
     lines:[
       {w:"N", fr:"Le lendemain, Margaux t'attend devant la boulangerie. Elle a l'air triste.", en:"The next day, Margaux is waiting for you in front of the bakery. She looks sad."},
       {w:"M", fr:"J'ai un grand problème. J'ai oublié ma recette du pain de campagne !", en:"I have a big problem. I've forgotten my country bread recipe!"},
       {w:"M", fr:"Je connais la farine et l'eau, mais un mot a disparu de ma tête.", en:"I know the flour and the water, but one word has disappeared from my head."},
       {w:"M", fr:"C'est blanc, on en met un peu, et la mer en a beaucoup !", en:"It's white, we add a little, and the sea has plenty!"},
       {w:"?", c:[
         ["C'est le sel, non ?", "It's the salt, isn't it?", 1],
         ["C'est le sucre, non ?", "It's the sugar, isn't it?", 0],
         ["C'est le beurre, non ?", "It's the butter, isn't it?", 0]]},
       {w:"M", fr:"Oui, le sel ! Merci, {nom}. Je me souviens maintenant.", en:"Yes, salt! Thank you, {nom}. I remember now."},
       {w:"N", fr:"Dans le Cahier, un petit mot brille : sel. Le mot est de retour.", en:"In the Notebook, a small word glows: sel. The word is back."},
       {w:"N", fr:"Dehors, la Brume recule un peu. Sur le panneau, la lettre U revient : BOULANGERIE !", en:"Outside, the Mist pulls back a little. On the sign, the letter U comes back: BOULANGERIE!"},
       {w:"M", fr:"Tu as sauvé mon sel et mon panneau ! Prends ce croissant, il est pour toi.", en:"You saved my salt and my sign! Take this croissant, it's for you."}
     ],
     cards:[
       {s:"Je connais la farine et l'___, mais un mot a disparu de ma tête.", a:"eau", d:["arbre","hôtel","oreille"], g:"I know the flour and the water, but one word has disappeared from my head."},
       {s:"C'est blanc, on en met un peu, et la mer en a ___ !", a:"beaucoup", d:["peu","chaque","toutes"], g:"It's white, we add a little, and the sea has plenty!"},
       {s:"Je me ___ maintenant.", a:"souviens", d:["souvient","souvenir","souvenu"], g:"I remember now."}
     ],
     hook:"Ce soir, Maître Encrier veut te montrer le secret des pierres.", hookEn:"Tonight, Master Inkwell wants to show you the secret of the stones.",
     resume:"{nom} a aidé Margaux à retrouver le mot « sel » ; la Brume a reculé et la lettre U est revenue sur le panneau."},

    {id:"p03", ch:1, lv:2, titre:"Le pont de pierres", titreEn:"The stone bridge",
     lieu:"L'atelier · le soir", lieuEn:"The workshop · evening",
     lines:[
       {w:"N", fr:"Ce soir-là, la pluie tombe sur l'atelier. Maître Encrier prépare du thé.", en:"That evening, rain falls on the workshop. Master Inkwell is making tea."},
       {w:"E", fr:"Tu as bien travaillé aujourd'hui, {nom}. Le sel est revenu.", en:"You worked well today, {nom}. The salt is back."},
       {w:"E", fr:"Mais attention : un mot sauvé aujourd'hui peut disparaître demain.", en:"But careful: a word saved today can disappear tomorrow."},
       {w:"E", fr:"Pour garder un mot, que faut-il faire, à ton avis ?", en:"To keep a word, what do you have to do, in your opinion?"},
       {w:"?", c:[
         ["Il faut le revoir demain, puis dans quelques jours.", "You have to see it again tomorrow, then in a few days.", 1],
         ["Il faut le lire une seule fois, très fort.", "You have to read it just once, very hard.", 0],
         ["Il ne faut plus jamais y penser.", "You must never think about it again.", 0]]},
       {w:"E", fr:"Exactement ! Un mot qu'on revoit au bon moment devient une pierre.", en:"Exactly! A word you see again at the right moment becomes a stone."},
       {w:"E", fr:"Avec assez de pierres, nous allons construire un pont sur la rivière.", en:"With enough stones, we're going to build a bridge over the river."},
       {w:"N", fr:"Par la fenêtre, tu vois une vieille bibliothèque, de l'autre côté de l'eau. Elle dort dans la brume.", en:"Through the window, you see an old library on the other side of the water. It sleeps in the mist."},
       {w:"E", fr:"Demain, le facteur arrive. Il est toujours en retard !", en:"Tomorrow, the postman arrives. He's always late!"}
     ],
     cards:[
       {s:"Un mot qu'on revoit au bon ___ devient une pierre.", a:"moment", d:["pont","thé","jardin"], g:"A word you see again at the right moment becomes a stone."},
       {s:"Avec assez de pierres, nous ___ construire un pont sur la rivière.", a:"allons", d:["allez","vont","va"], g:"With enough stones, we're going to build a bridge over the river."},
       {s:"Un mot sauvé aujourd'hui peut ___ demain.", a:"disparaître", d:["disparu","disparaît","disparais"], g:"A word saved today can disappear tomorrow."}
     ],
     hook:"Demain, un jeune facteur arrive très vite… et très en retard.", hookEn:"Tomorrow, a young postman arrives very fast… and very late.",
     resume:"Maître Encrier a expliqué que les mots revus au bon moment deviennent des pierres pour bâtir un pont vers la vieille bibliothèque, où dort la Brume."},

    {id:"p04", ch:2, lv:2, titre:"Le facteur arrive", titreEn:"The postman arrives",
     lieu:"Devant l'atelier · le matin", lieuEn:"In front of the workshop · morning",
     lines:[
       {w:"N", fr:"Tu entends une sonnette. Un jeune homme arrive à vélo, très vite.", en:"You hear a bell. A young man arrives on a bike, very fast."},
       {w:"T", fr:"Désolé, désolé ! Je suis en retard. Je m'appelle Théo, je suis le facteur !", en:"Sorry, sorry! I'm late. My name is Théo, I'm the postman!"},
       {w:"T", fr:"J'ai vingt lettres pour le village, mais je ne peux plus lire les adresses.", en:"I have twenty letters for the village, but I can't read the addresses any more."},
       {w:"N", fr:"Tu regardes une enveloppe. Le nom de la rue a disparu.", en:"You look at an envelope. The street name has disappeared."},
       {w:"T", fr:"Je sais seulement que c'est la rue où l'on achète des fruits, des légumes et du fromage.", en:"I only know it's the street where you buy fruit, vegetables and cheese."},
       {w:"?", c:[
         ["C'est la rue du Marché !", "It's Market Street!", 1],
         ["C'est la rue de la Gare !", "It's Station Street!", 0],
         ["C'est la rue de l'École !", "It's School Street!", 0]]},
       {w:"T", fr:"Mais oui ! Tu es génial, {nom}.", en:"Of course! You're brilliant, {nom}."},
       {w:"N", fr:"Ensemble, vous partez livrer les lettres. Tu apprends le nom des rues, des magasins et des gens.", en:"Together, you set off to deliver the letters. You learn the names of streets, shops and people."},
       {w:"T", fr:"Tiens, une dernière lettre pour Maître Encrier. Elle vient de très loin.", en:"Here, one last letter for Master Inkwell. It comes from very far away."},
       {w:"N", fr:"Sur l'enveloppe, il y a un timbre rouge et un seul mot : URGENT.", en:"On the envelope, there is a red stamp and a single word: URGENT."}
     ],
     cards:[
       {s:"Je m'appelle Théo, je suis le ___ !", a:"facteur", d:["pont","soleil","fromage"], g:"My name is Théo, I'm the postman!"},
       {s:"J'ai vingt ___ pour le village, mais je ne peux plus lire les adresses.", a:"lettres", d:["pommes","chaises","mois"], g:"I have twenty letters for the village, but I can't read the addresses any more."},
       {s:"C'est la rue où l'on ___ des fruits, des légumes et du fromage.", a:"achète", d:["achètes","acheter","acheté"], g:"It's the street where you buy fruit, vegetables and cheese."}
     ],
     hook:"Une lettre urgente est arrivée pour Maître Encrier. Que dit-elle ?", hookEn:"An urgent letter has arrived for Master Inkwell. What does it say?",
     resume:"Théo, le facteur en retard, ne pouvait plus lire les adresses ; {nom} l'a aidé, puis il a apporté une lettre urgente pour Maître Encrier."},

    {id:"p05", ch:2, lv:2, titre:"La lettre urgente", titreEn:"The urgent letter",
     lieu:"L'atelier · midi", lieuEn:"The workshop · midday",
     lines:[
       {w:"N", fr:"Maître Encrier ouvre la lettre. Ses mains tremblent un peu.", en:"Master Inkwell opens the letter. His hands tremble a little."},
       {w:"E", fr:"C'est une lettre de la ville. Elle dit : « Venez vite. La Brume est dans la gare. »", en:"It's a letter from the city. It says: 'Come quickly. The Mist is at the station.'"},
       {w:"T", fr:"La gare ? Le train part demain matin, à huit heures dix.", en:"The station? The train leaves tomorrow morning, at ten past eight."},
       {w:"E", fr:"{nom}, tu as bien écouté ? Quand part le train ?", en:"{nom}, did you listen well? When does the train leave?"},
       {w:"?", c:[
         ["Demain matin, à huit heures dix.", "Tomorrow morning, at ten past eight.", 1],
         ["Hier soir, à dix heures.", "Last night, at ten o'clock.", 0],
         ["Je ne sais pas, j'ai faim.", "I don't know, I'm hungry.", 0]]},
       {w:"E", fr:"Très bien. Prépare ton sac : un manteau, un parapluie et ton Cahier.", en:"Very good. Prepare your bag: a coat, an umbrella and your Notebook."},
       {w:"N", fr:"Tu mets ton Cahier dans le sac. Tu sens qu'une grande aventure commence.", en:"You put your Notebook in the bag. You feel that a great adventure is beginning."},
       {w:"T", fr:"Moi, je viens avec vous ! Les lettres peuvent attendre un peu.", en:"I'm coming with you! The letters can wait a little."},
       {w:"E", fr:"D'accord. Mais ce soir, on dort. Demain, nous partons à l'aube.", en:"All right. But tonight, we sleep. Tomorrow, we leave at dawn."}
     ],
     cards:[
       {s:"Le train part demain ___, à huit heures dix.", a:"matin", d:["hier","hiver","maison"], g:"The train leaves tomorrow morning, at ten past eight."},
       {s:"Prépare ton sac : un manteau, un ___ et ton Cahier.", a:"parapluie", d:["jardin","rivière","soleil"], g:"Prepare your bag: a coat, an umbrella and your Notebook."},
       {s:"Les lettres peuvent ___ un peu.", a:"attendre", d:["attendu","attends","attend"], g:"The letters can wait a little."}
     ],
     hook:"Cette nuit, quelqu'un écoute derrière la fenêtre…", hookEn:"Tonight, someone is listening behind the window…",
     resume:"Une lettre de la ville annonce que la Brume est dans la gare ; Maître Encrier, Théo et {nom} prendront le train le lendemain matin."},

    {id:"p06", ch:2, lv:2, titre:"La nuit de la Brume", titreEn:"The night of the Mist",
     lieu:"L'atelier · la nuit", lieuEn:"The workshop · night",
     lines:[
       {w:"N", fr:"La nuit est silencieuse. Tu ne dors pas bien. Tu écoutes la pluie.", en:"The night is silent. You don't sleep well. You listen to the rain."},
       {w:"N", fr:"Soudain, une voix très douce parle derrière la fenêtre.", en:"Suddenly, a very soft voice speaks behind the window."},
       {w:"B", fr:"Oublie… oublie… Tu es fatigué. Tu n'as pas besoin de ces mots.", en:"Forget… forget… You're tired. You don't need those words."},
       {w:"N", fr:"Une petite lumière blanche entre dans la chambre. Ton Cahier est ouvert sur la table.", en:"A small white light comes into the room. Your Notebook is open on the table."},
       {w:"?", c:[
         ["Je lis les mots du Cahier à voix haute.", "I read the Notebook's words aloud.", 1],
         ["Je ferme les yeux et je dors.", "I close my eyes and sleep.", 0],
         ["J'ouvre la fenêtre pour parler à la Brume.", "I open the window to talk to the Mist.", 0]]},
       {w:"N", fr:"Tu lis : sel… souviens… moment… allons… Chaque mot brille comme une petite étoile.", en:"You read: salt… remember… moment… let's go… Each word shines like a little star."},
       {w:"B", fr:"Non… pas ça… Ces mots… sont trop forts…", en:"No… not that… These words… are too strong…"},
       {w:"N", fr:"La lumière blanche recule et sort par la fenêtre. Dehors, la pluie s'arrête.", en:"The white light pulls back and goes out through the window. Outside, the rain stops."},
       {w:"N", fr:"Maître Encrier est à la porte, avec sa lampe.", en:"Master Inkwell is at the door, with his lamp."},
       {w:"E", fr:"Tu n'as pas oublié. C'est ton premier vrai combat, {nom}, et tu l'as gagné.", en:"You didn't forget. It's your first real fight, {nom}, and you won it."},
       {w:"E", fr:"Demain, nous partons pour la gare. L'acte deux commence.", en:"Tomorrow, we leave for the station. Act two begins."}
     ],
     cards:[
       {s:"Une petite lumière blanche ___ dans la chambre.", a:"entre", d:["entres","entrer","entré"], g:"A small white light comes into the room."},
       {s:"Je lis les mots du Cahier à ___ haute.", a:"voix", d:["voie","vois","fois"], g:"I read the Notebook's words aloud."},
       {s:"Tu n'as pas ___.", a:"oublié", d:["oublier","oublie","oublies"], g:"You haven't forgotten."}
     ],
     hook:"Fin de l'acte I. À la gare, la Brume t'attend.", hookEn:"End of Act I. At the station, the Mist is waiting for you.",
     resume:"La Brume est venue la nuit ; {nom} l'a repoussée en lisant à voix haute les mots du Cahier."}
    ,

    {id:"p07", ch:3, lv:2, titre:"Le quai", titreEn:"The platform",
     lieu:"La gare de Plume · l'aube", lieuEn:"Plume station · dawn",
     lines:[
       {w:"N", fr:"À l'aube, tu marches avec Maître Encrier et Théo vers la petite gare.", en:"At dawn, you walk with Master Inkwell and Théo to the little station."},
       {w:"N", fr:"Il fait froid. Le quai est presque vide.", en:"It's cold. The platform is almost empty."},
       {w:"T", fr:"Le train est en retard ? Pour une fois, ce n'est pas moi !", en:"The train is late? For once, it's not me!"},
       {w:"E", fr:"Ne rigole pas, Théo. Nous avons besoin de trois billets pour la ville.", en:"Don't laugh, Théo. We need three tickets for the city."},
       {w:"N", fr:"Au guichet, un employé range des papiers sans lever la tête.", en:"At the ticket window, a clerk is tidying papers without looking up."},
       {w:"?", c:[
         ["Bonjour ! Trois billets pour la ville, s'il vous plaît.", "Hello! Three tickets for the city, please.", 1],
         ["Bonjour ! Je voudrais une baguette, s'il vous plaît.", "Hello! I would like a baguette, please.", 0],
         ["Bonsoir ! Où est la boulangerie ?", "Good evening! Where is the bakery?", 0]]},
       {w:"N", fr:"L'employé te donne les billets. Ça fait trente-six euros.", en:"The clerk gives you the tickets. That's thirty-six euros."},
       {w:"E", fr:"Garde bien ces billets, {nom}. Sans billet, pas de voyage.", en:"Keep these tickets safe, {nom}. No ticket, no journey."},
       {w:"N", fr:"Tu regardes le grand panneau de la gare. Le nom de la gare n'est plus écrit.", en:"You look at the station's big sign. The station's name is no longer written."},
       {w:"T", fr:"Regardez ! Le panneau est blanc. La Brume est déjà là !", en:"Look! The sign is blank. The Mist is already here!"},
       {w:"N", fr:"Au loin, tu entends le train arriver.", en:"In the distance, you hear the train arriving."}
     ],
     cards:[
       {s:"Bonjour ! Trois ___ pour la ville, s'il vous plaît.", a:"billets", d:["pommes","fenêtres","nuages"], g:"Hello! Three tickets for the city, please."},
       {s:"Pour une ___, ce n'est pas moi !", a:"fois", d:["voix","fin","mer"], g:"For once, it's not me!"},
       {s:"Sans billet, pas de ___.", a:"voyage", d:["fromage","soleil","manteau"], g:"No ticket, no journey."}
     ],
     hook:"Dans le train, un voyageur très étrange est assis tout seul…", hookEn:"On the train, a very strange traveller is sitting all alone…",
     resume:"Maître Encrier, Théo et {nom} ont acheté trois billets pour la ville ; le panneau de la gare de Plume avait déjà perdu son nom."},

    {id:"p08", ch:3, lv:2, titre:"Le voyageur sans nom", titreEn:"The traveller with no name",
     lieu:"Le train · le matin", lieuEn:"The train · morning",
     lines:[
       {w:"N", fr:"Le train part à huit heures dix. Tu t'assois près de la fenêtre.", en:"The train leaves at ten past eight. You sit down by the window."},
       {w:"N", fr:"En face de toi, un vieux monsieur serre une valise contre lui.", en:"Opposite you, an old gentleman is holding a suitcase tight against him."},
       {w:"V", fr:"Excusez-moi… Est-ce que vous savez comment je m'appelle ?", en:"Excuse me… do you know what my name is?"},
       {w:"T", fr:"Quoi ? Vous ne savez pas votre propre nom ?", en:"What? You don't know your own name?"},
       {w:"V", fr:"J'avais un nom ce matin. Il est parti avec la Brume.", en:"I had a name this morning. It left with the Mist."},
       {w:"E", fr:"Calmez-vous, monsieur. Regardons sa valise : il y a peut-être une étiquette.", en:"Calm down, sir. Let's look at the suitcase: there may be a label."},
       {w:"N", fr:"Sur la valise, il y a une étiquette. Mais les lettres sont presque effacées : P, E, R, D, U.", en:"On the suitcase there is a label. But the letters are almost erased: P, E, R, D, U."},
       {w:"?", c:[
         ["Monsieur, je crois que vous vous appelez Perdu.", "Sir, I think your name is Perdu.", 1],
         ["Monsieur, je crois que vous vous appelez Pardon.", "Sir, I think your name is Pardon.", 0],
         ["Monsieur, vous n'avez pas de nom.", "Sir, you don't have a name.", 0]]},
       {w:"V", fr:"Perdu ! Oui, c'est ça ! Je suis Monsieur Perdu. Merci mille fois !", en:"Perdu! Yes, that's it! I'm Mr. Perdu. Thanks a thousand times!"},
       {w:"N", fr:"Dans ton Cahier, un nouveau mot brille : « étiquette ».", en:"In your Notebook, a new word glows: “étiquette”."},
       {w:"E", fr:"Tu vois, {nom} ? Aider les autres à se souvenir, c'est aussi se souvenir soi-même.", en:"You see, {nom}? Helping others remember is also remembering yourself."}
     ],
     cards:[
       {s:"Est-ce que vous ___ comment je m'appelle ?", a:"savez", d:["savons","sais","savoir"], g:"Do you know what my name is?"},
       {s:"Il est ___ avec la Brume.", a:"parti", d:["partir","partie","partis"], g:"It left with the Mist."},
       {s:"Merci ___ fois !", a:"mille", d:["milles","mil","millième"], g:"Thanks a thousand times!"}
     ],
     hook:"Le train s'arrête. Mais personne ne dit le nom de la gare…", hookEn:"The train stops. But nobody says the station's name…",
     resume:"Dans le train, {nom} a aidé M. Perdu à retrouver son nom grâce à l'étiquette de sa valise."},

    {id:"p09", ch:3, lv:2, titre:"La gare grise", titreEn:"The grey station",
     lieu:"La gare de la ville · midi", lieuEn:"The city station · midday",
     lines:[
       {w:"N", fr:"Le train arrive dans une grande gare. Mais il y a un problème : tout est gris.", en:"The train arrives in a big station. But there is a problem: everything is grey."},
       {w:"N", fr:"Les panneaux sont blancs. Les horloges sont arrêtées. Les gens marchent sans parler.", en:"The signs are blank. The clocks have stopped. People walk without speaking."},
       {w:"T", fr:"On dirait une gare dans un rêve. Où sont les noms des quais ?", en:"It looks like a station in a dream. Where are the platform names?"},
       {w:"E", fr:"Cherchons le chef de gare. Il connaît sûrement les noms.", en:"Let's look for the stationmaster. He surely knows the names."},
       {w:"N", fr:"Au bout du quai, un homme en uniforme regarde le ciel. Il tient un sifflet.", en:"At the end of the platform, a man in uniform looks at the sky. He is holding a whistle."},
       {w:"?", c:[
         ["Bonjour, monsieur. Vous êtes le chef de gare ?", "Hello, sir. Are you the stationmaster?", 1],
         ["Bonjour, monsieur. Vous êtes le boulanger ?", "Hello, sir. Are you the baker?", 0],
         ["Au revoir, monsieur. Où est mon train ?", "Goodbye, sir. Where is my train?", 0]]},
       {w:"C", fr:"Oui. Mais depuis ce matin, je ne sais plus le nom de ma gare.", en:"Yes. But since this morning, I no longer know my station's name."},
       {w:"C", fr:"Sans nom, les trains ne savent pas où s'arrêter. C'est dangereux !", en:"Without a name, trains don't know where to stop. It's dangerous!"},
       {w:"E", fr:"Nous allons le retrouver. Donnez-nous un indice.", en:"We will find it. Give us a clue."},
       {w:"C", fr:"Le nom commence par un grand M, et on le trouve sur la vieille horloge du hall.", en:"The name starts with a capital M, and you'll find it on the old clock in the hall."},
       {w:"N", fr:"Tu lèves les yeux. Au-dessus de toi, une très vieille horloge dort dans la brume.", en:"You look up. Above you, a very old clock sleeps in the mist."}
     ],
     cards:[
       {s:"Depuis ce matin, je ne sais plus le ___ de ma gare.", a:"nom", d:["prix","train","jour"], g:"Since this morning, I no longer know my station's name."},
       {s:"Sans nom, les trains ne savent pas où ___.", a:"s'arrêter", d:["arrêter","arrêté","s'arrête"], g:"Without a name, trains don't know where to stop."},
       {s:"Il connaît ___ les noms.", a:"sûrement", d:["sûr","sûre","sûrs"], g:"He surely knows the names."}
     ],
     hook:"Sur l'horloge, un nom brille à peine… mais la Brume est plus rapide que toi.", hookEn:"On the clock, a name barely glows… but the Mist is faster than you.",
     resume:"À la gare de la ville tout était gris ; le chef de gare avait oublié le nom de sa gare, qu'il faut chercher sur la vieille horloge du hall."},

    {id:"p10", ch:4, lv:2, titre:"L'horloge muette", titreEn:"The silent clock",
     lieu:"Le hall de la gare · l'après-midi", lieuEn:"The station hall · afternoon",
     lines:[
       {w:"N", fr:"Tu montes l'escalier de l'horloge avec le chef de gare. Chaque marche est froide.", en:"You climb the clock's stairs with the stationmaster. Each step is cold."},
       {w:"N", fr:"En haut, les aiguilles sont arrêtées à midi dix.", en:"At the top, the hands are stopped at ten past twelve."},
       {w:"C", fr:"Voilà le cadran. Il y avait notre nom ici, en lettres d'or.", en:"There is the dial. Our name used to be here, in golden letters."},
       {w:"N", fr:"Tu lis le cadran. Il reste des traces : M, O, N, T, puis L, U, I…", en:"You read the dial. Some traces remain: M, O, N, T, then L, U, I…"},
       {w:"T", fr:"Mont… et après ? Montréal ? Montmartre ?", en:"Mont… and then? Montréal? Montmartre?"},
       {w:"?", c:[
         ["Non, regardez : c'est Montluisant !", "No, look: it's Montluisant!", 1],
         ["Non, regardez : c'est Montréal !", "No, look: it's Montréal!", 0],
         ["Non, regardez : c'est Montmartre !", "No, look: it's Montmartre!", 0]]},
       {w:"N", fr:"Dès que tu dis le nom, les lettres reviennent une à une.", en:"As soon as you say the name, the letters come back one by one."},
       {w:"N", fr:"Elles brillent comme de l'or sur le cadran. Les aiguilles tremblent, puis elles repartent. Tic, tac, tic, tac.", en:"They shine like gold on the dial. The hands tremble, then start again. Tick, tock, tick, tock."},
       {w:"C", fr:"Merci ! Vous avez sauvé ma gare et mes horaires.", en:"Thank you! You have saved my station and my timetables."},
       {w:"E", fr:"Pas encore, chef. Écoutez : quelqu'un rit en bas, dans le hall.", en:"Not yet, chief. Listen: someone is laughing downstairs, in the hall."}
     ],
     cards:[
       {s:"En haut, les aiguilles sont ___ à midi dix.", a:"arrêtées", d:["arrêter","arrêtés","arrêtée"], g:"At the top, the hands are stopped at ten past twelve."},
       {s:"Dès que tu dis le nom, les lettres reviennent une à ___.", a:"une", d:["un","uns","unes"], g:"As soon as you say the name, the letters come back one by one."},
       {s:"Merci ! Vous avez ___ ma gare et mes horaires.", a:"sauvé", d:["sauver","sauvez","sauvés"], g:"Thank you! You have saved my station and my timetables."}
     ],
     hook:"Un rire froid résonne dans le hall. Ce n'est pas un rire d'enfant…", hookEn:"A cold laugh echoes in the hall. It is not a child's laugh…",
     resume:"{nom} a lu les traces sur l'horloge et dit le nom de la gare, Montluisant, qui est revenu en lettres d'or ; mais un rire inquiétant résonne dans le hall."},

    {id:"p11", ch:4, lv:2, titre:"Le tableau noir", titreEn:"The black board",
     lieu:"Le hall · le soir", lieuEn:"The hall · evening",
     lines:[
       {w:"N", fr:"Dans le grand hall, une foule regarde le tableau des départs. Il est complètement noir.", en:"In the big hall, a crowd looks at the departures board. It is completely black."},
       {w:"N", fr:"Un rire froid résonne sous le plafond. Une fumée blanche passe entre les gens.", en:"A cold laugh echoes under the ceiling. White smoke drifts between the people."},
       {w:"B", fr:"Plus d'horaires, plus de trains, plus de voyages… Quel beau silence !", en:"No more timetables, no more trains, no more journeys… What a beautiful silence!"},
       {w:"T", fr:"C'est la Brume ! Elle veut arrêter tous les trains.", en:"It's the Mist! It wants to stop all the trains."},
       {w:"C", fr:"Je me souviens de trois horaires. La mer, à neuf heures et demie.", en:"I remember three times. The sea, at half past nine."},
       {w:"C", fr:"La montagne, à midi. La forêt, à quinze heures.", en:"The mountain, at noon. The forest, at three in the afternoon."},
       {w:"V", fr:"Pour la montagne, c'est à quelle heure ? Je dois partir !", en:"For the mountain, what time is it? I have to leave!"},
       {w:"?", c:[
         ["Le train pour la montagne part à midi.", "The train for the mountain leaves at noon.", 1],
         ["Le train pour la montagne part à minuit.", "The train for the mountain leaves at midnight.", 0],
         ["Le train pour la montagne part à neuf heures et demie.", "The train for the mountain leaves at half past nine.", 0]]},
       {w:"N", fr:"Le tableau s'allume. Les chiffres brillent un par un.", en:"The board lights up. The numbers shine one by one."},
       {w:"N", fr:"La Brume pousse un cri de rage et recule dans l'ombre.", en:"The Mist lets out a cry of rage and retreats into the shadows."},
       {w:"E", fr:"Bravo, {nom}. Tu as bien écouté, tu as bien écrit, et tu t'es bien souvenu.", en:"Well done, {nom}. You listened well, you wrote well, and you remembered well."}
     ],
     cards:[
       {s:"Un rire froid ___ sous le plafond.", a:"résonne", d:["résonner","résonné","résonnes"], g:"A cold laugh echoes under the ceiling."},
       {s:"La mer, à neuf heures et ___.", a:"demie", d:["demi","moitié","moins"], g:"The sea, at half past nine."},
       {s:"La Brume pousse un cri de rage et ___ dans l'ombre.", a:"recule", d:["reculer","reculé","reculent"], g:"The Mist lets out a cry of rage and retreats into the shadows."}
     ],
     hook:"Ce soir, la Brume prend une forme. Elle veut te parler.", hookEn:"Tonight, the Mist takes on a shape. It wants to talk to you.",
     resume:"Dans le hall, la Brume a noirci le tableau des départs ; {nom} a retrouvé les horaires de trois trains et la Brume a reculé."},

    {id:"p12", ch:4, lv:2, titre:"Le premier mot", titreEn:"The first word",
     lieu:"Le hall · la nuit", lieuEn:"The hall · night",
     lines:[
       {w:"N", fr:"La nuit tombe sur la gare. Le hall est maintenant plein de voyageurs qui parlent, rient et se souviennent.", en:"Night falls on the station. The hall is now full of travellers who talk, laugh and remember."},
       {w:"N", fr:"Au milieu du hall, une fumée blanche se rassemble. Elle prend la forme d'une grande silhouette.", en:"In the middle of the hall, white smoke gathers. It takes the shape of a tall silhouette."},
       {w:"B", fr:"Bravo, petit apprenti. Tu as sauvé un nom, une gare et des horaires.", en:"Bravo, little apprentice. You saved a name, a station and some timetables."},
       {w:"B", fr:"Mais ce n'est pas ça que je cherche. Je cherche le premier mot de ton Cahier.", en:"But that's not what I'm looking for. I'm looking for the first word of your Notebook."},
       {w:"E", fr:"Le premier mot ? Pourquoi veux-tu le premier mot ?", en:"The first word? Why do you want the first word?"},
       {w:"B", fr:"Parce que, sans le premier mot, aucun autre mot ne tient.", en:"Because, without the first word, no other word holds."},
       {w:"N", fr:"Tu ouvres ton Cahier. La première page est presque blanche. Il reste une seule ligne, très pâle.", en:"You open your Notebook. The first page is almost white. Only one line is left, very pale."},
       {w:"?", c:[
         ["Je lis la ligne à voix haute.", "I read the line aloud.", 1],
         ["Je ferme le Cahier et je pars.", "I close the Notebook and leave.", 0],
         ["Je donne le Cahier à la Brume.", "I give the Notebook to the Mist.", 0]]},
       {w:"N", fr:"Tu lis : « Je me souviens ». Ces trois mots brillent plus fort que tous les autres.", en:"You read: “I remember”. These three words shine brighter than all the others."},
       {w:"B", fr:"Non… pas ces mots… pas encore…", en:"No… not those words… not yet…"},
       {w:"N", fr:"La silhouette se défait et disparaît dans les rails. Le silence revient.", en:"The silhouette comes apart and vanishes into the rails. Silence returns."},
       {w:"E", fr:"Tu as gagné cette nuit, {nom}. Mais la Brume reviendra. Demain, nous cherchons où elle dort.", en:"You won tonight, {nom}. But the Mist will return. Tomorrow, we look for where it sleeps."}
     ],
     cards:[
       {s:"Au milieu du hall, une fumée blanche se ___.", a:"rassemble", d:["rassembler","rassemblé","rassemblent"], g:"In the middle of the hall, white smoke gathers."},
       {s:"Parce que, sans le premier mot, ___ autre mot ne tient.", a:"aucun", d:["plusieurs","quelques","beaucoup"], g:"Because, without the first word, no other word holds."},
       {s:"La silhouette se défait et ___ dans les rails.", a:"disparaît", d:["disparaître","disparu","disparais"], g:"The silhouette comes apart and vanishes into the rails."}
     ],
     hook:"Fin de l'acte II. Demain, tu pars à la recherche de la Brume, de l'autre côté de l'eau.", hookEn:"End of Act II. Tomorrow, you set off to find the Mist, on the other side of the water.",
     resume:"À la gare, la Brume a demandé à {nom} le premier mot du Cahier ; {nom} a lu à voix haute « Je me souviens », et la Brume a reculé."}
  ]
};
