import vk_api
import random
import nltk
from vk_api.longpoll import VkLongPoll, VkEventType
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from BOT_CONFIG import BOT_CONFIG
from vk_api.utils import get_random_id
from keyboard import menu_keyboard, time_keyboard, study_keyboard, session_keyboard, grant_keyboard, map_keyboard, another_keyboard, other_keyboard, food_keyboard, docs_keyboard, studentlife_keyboard, health_keyboard, nonresident_keyboard, mugs_keyboard, sport_keyboard, menu_keyboard_en, menu_keyboard_en_next
#! /usr/bin/env python
# -*- coding: utf-8 -*-
X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        X_text.append(example)
        y.append(intent)

# vectorizer = CountVectorizer(analyzer='char', ngram_range=(3,3))
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3,3))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X, y)

def clear_phrase (phrase):
    phrase = phrase.lower()

    alphabet = 'йцукенгшщзхъфывапролджэячсмитьбюqwertyuiopasdfghjklzxcvbnm- '
    result = ''.join(symbol for symbol in phrase if symbol in alphabet)

    for symbol in result:
        if symbol == 'ё':
            symbol = 'е'

    return result.strip()

def classify_intent (replica):
    replica = clear_phrase(replica)
    intent=clf.predict(vectorizer.transform([replica]))[0]

    for example in BOT_CONFIG['intents'][intent]['examples']:
        example = clear_phrase(example)
        distance = nltk.edit_distance(replica, example)
        if example and distance / len(example) < 0.4:
            return intent


def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        return random.choice(responses)

with open("dialogues.txt", "r", encoding="utf-8") as f:
    content = f.read()

dialogues_str=content.split('\n\n')
dialogues = [dialogue_str.split('\n')[:2] for dialogue_str in dialogues_str] #Список списков вопрос ответ из датасета

dialogues_filtered = []
questions = set()

for dialogue in dialogues: #Чистим от всех диалогов, у которых реплик не 2
    if len(dialogue) != 2:
        continue
    question, answer = dialogue
    question = clear_phrase(question[2:]) #Берется вопрос
    answer = answer[2:] #Берётся ответ
    if question != '' and question not in questions:
        questions.add(question)
        dialogues_filtered.append([question, answer])

dialogues_structured={} #Создаем новый словарь по словам
for question, answer in dialogues_filtered:
    words = set(question.split(' '))
    for word in words:
        if word not in dialogues_structured:
            dialogues_structured[word]=[]
        dialogues_structured[word].append([question, answer])

def send_replica(replica):
    f=open("out.txt", "a")
    f.write(replica)
    f.write("\n")
    f.close()

def generate_answer(replica):
    replica = clear_phrase(replica)
    words = set(replica.split(' ')) #Разделение replica на слова
    mini_dataset = []
    for word in words:
        if word in dialogues_structured:
        #if word in dialogues_structured_cut:
            mini_dataset += dialogues_structured[word]
            #mini_dataset+=dialogues_structured_cut[word] #Список пар вопросов и ответов

    answers = [] #[[distance_weighted, question, answer]]
    for question, answer in mini_dataset:
        if abs(len(replica) - len(question))/len(question) < 0.3: #минимальное расстояние ливенштейна
            distance = nltk.edit_distance(replica, question)
            distance_weighted=distance/len(question)
            if distance / len(question) < 0.4:
                answers.append([distance_weighted, question, answer])
    if answers:
        return min(answers, key=lambda three: three[0])[2]

def get_failure_phrase():
    failure_phrases=BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

#def get_failure_phrase_eng():
#    failure_phrases=BOT_CONFIG['failure_phrases_eng']
#    return random.choice(failure_phrases)


stats = {'intent':0, 'generate':0, 'failure': 0}

def bot(replica):
    intent = classify_intent(replica)
    if intent:
        answer = get_answer_by_intent(intent)
        if answer:
            stats['intent'] += 1
            return answer
    answer = generate_answer(replica)
    if answer:
        stats['generate'] += 1
        return answer
    stats['failure'] += 1
    if not intent and not answer:
        send_replica(replica)
    return get_failure_phrase()

class MyLongPoll (VkLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                pass

token = "de5961af36780f4d9758647f092a04862a1a1a431f532ad720661928ef5826eb4e0ffcb93b31457d2d64b"
vk_session = vk_api.VkApi(token=token)
vk_session._auth_token()
longpoll = MyLongPoll(vk_session)

session_api = vk_session.get_api()
#longpoll = VkLongPoll(vk_session)

cats = ["photo-203034678_457239030", "photo-203034678_457239037", "photo-203034678_457239038", "photo-203034678_457239039", "photo-203034678_457239049", "photo-203034678_457239050", "photo-203034678_457239051", "photo-203034678_457239052", "photo-203034678_457239053", "photo-203034678_457239054", "photo-203034678_457239055", "photo-203034678_457239056", "photo-203034678_457239057", "photo-203034678_457239058", "photo-203034678_457239059", "photo-203034678_457239060", "photo-203034678_457239061"]
inf_1 = "photo-203034678_457239046"
inf_2 = "photo-203034678_457239048"
#inf_10 = ""
#inf_11
beach_1 = "photo-203034678_457239062"
beach_2 = "photo-203034678_457239063"
'''#ЗАГРУЗКАФОТОК
uploader = vk_api.upload.VkUpload(vk_session)
img=uploader.photo_messages("Взрослое.PNG")
print(img)
media_id=str(img[0]['id'])
owner_id=str(img[0]['owner_id'])
print("photo"+owner_id+"_"+media_id)
'''

class User():
    def __init__(self, id, mode, level):
        self.id = id
        self.mode = mode
        self.level = level

def check_registration(id):
    members = vk_session.method('groups.getMembers', {'group_id': 203034678})['items']
    return (id in members)

def check(x):
    file=open('data.txt', 'r', encoding='utf-8')
    flag=0
    if str(x) in file.read():
        flag=1
    return flag
    file.close()

def adder(x):
    file=open('data.txt', 'a', encoding='utf-8')
    file.write(f'{x}\n')
    file.close()

#key_intents = ["study_key", "session_key", "grant_key", "map_key", "food_key", "another_key", "docs_key", "time_key", "other_key", "away_key", "studentlife_key", "nonresident_key", "mugs_key", "sport_key", "health_key"]

def check_intent(text):
    #for intent in key_intents:
    #   if classify_intent(text) != intent:
    #        temp = 0
    #    else:
    #        temp = 1
    #return temp
    if classify_intent(text) != "study_key" and classify_intent(text) != "session_key" and classify_intent(text) != "grant_key" and classify_intent(text) != "map_key" and classify_intent(text) != "food_key" and classify_intent(text) != "another_key" and classify_intent(text) != "docs_key" and classify_intent(text) != "time_key" and classify_intent(text) != "other_key" and classify_intent(text) != "away_key" and classify_intent(text) != 'menu' and classify_intent(text) != 'studentlife_key' and classify_intent(text) != 'nonresident_key' and classify_intent(text) != 'mugs_key' and classify_intent(text) != 'sport_key' and classify_intent(text) != 'health_key' and classify_intent(text) != 'eng_menu_key' and classify_intent(text) != 'eng_menu_next_key':
        #print(classify_intent(text))
        return 0
    else:
        #print('1')
        return 1

def sender(id, text, key, flag_key):
    if flag_key == 1:
        vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard' : key.get_empty_keyboard(), 'dont_parse_links': 1})
    else:
        vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': get_random_id(), 'keyboard': key.get_keyboard()})

temp_keyboard = menu_keyboard

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            messages = vk_session.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})
            if messages["count"] >= 1:
                text = messages['items'][0]['last_message']['text']
                user_id = messages['items'][0]['last_message']['from_id']
                #vk_session.method("messages.send",{"user_id": user_id, "sticker_id": 1, "random_id": get_random_id()})
                if check_registration(user_id):
                    message = 'Выберите одну из категорий или задайте вопрос мне \nChoose one of the categories or ask me a question'
                    flag_key = 0
                    if classify_intent(text) == 'cats':
                        stats['intent'] += 1
                        vk_session.method("messages.send", {"user_id": user_id, "message": bot(text), "attachment": random.choice(cats), "random_id": get_random_id()})
                    elif classify_intent(text) == 'question31':
                        stats['intent'] += 1
                        vk_session.method("messages.send", {"user_id": user_id, "message": bot(text), "attachment": inf_1, "random_id": get_random_id()})
                    #elif classify_intent(text) == 'question100':
                    #    stats['intent'] += 1
                    #    vk_session.method("messages.send", {"user_id": user_id, "message": bot(text), "attachment": inf_10, "random_id": get_random_id()})
                    elif classify_intent(text) == 'question26':
                        stats['intent'] += 1
                        vk_session.method("messages.send", {"user_id": user_id, "message": "Лови <3", "attachment": inf_2, "random_id": get_random_id()})
                    elif classify_intent(text) == 'menu':
                        temp_keyboard = menu_keyboard
                    elif classify_intent(text) == 'study_key':
                        temp_keyboard = study_keyboard
                    elif classify_intent(text) == 'session_key':
                        temp_keyboard = session_keyboard
                    elif classify_intent(text) == 'grant_key':
                        temp_keyboard = grant_keyboard
                    elif classify_intent(text) == 'map_key':
                        temp_keyboard = map_keyboard
                    elif classify_intent(text) == 'food_key':
                        temp_keyboard = food_keyboard
                    elif classify_intent(text) == 'another_key':
                        temp_keyboard = another_keyboard
                    elif classify_intent(text) == 'docs_key':
                        temp_keyboard = docs_keyboard
                    elif classify_intent(text) == 'studentlife_key':
                        temp_keyboard = studentlife_keyboard
                    elif classify_intent(text) == 'health_key':
                        temp_keyboard = health_keyboard
                    elif classify_intent(text) == 'nonresident_key':
                        temp_keyboard = nonresident_keyboard
                    elif classify_intent(text) == 'time_key':
                        temp_keyboard = time_keyboard
                    elif classify_intent(text) == 'mugs_key':
                        temp_keyboard = mugs_keyboard
                    elif classify_intent(text) == 'sport_key':
                        temp_keyboard = sport_keyboard
                    elif classify_intent(text) == 'other_key':
                        temp_keyboard = other_keyboard
                    elif classify_intent(text) == 'away_key':
                        temp_keyboard = menu_keyboard
                    elif classify_intent(text) == 'eng_menu_key':
                        message = 'Choose one of the categories or ask me a question'
                        temp_keyboard = menu_keyboard_en
                    elif classify_intent(text) == 'eng_menu_next_key':
                        message = 'Choose one of the categories or ask me a question'
                        temp_keyboard = menu_keyboard_en_next
                    #elif classify_intent(text) == 'cleaning_key':
                     #   flag_key = 1
                    elif classify_intent(text) == 'menu':
                        flag_key = 0
                    if check_intent(text) == 1:
                        sender(user_id, message, temp_keyboard, flag_key)
                    else:
                        message_bot = bot(text)
                        sender(user_id, message_bot, temp_keyboard, flag_key)
                else:
                    text = 'Вы не подписаны на группу! \n Для того, чтобы пользоваться ботом, необходимо подписаться на сообщество!'
                    vk_session.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': get_random_id()})
                print(stats)
