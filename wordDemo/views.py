from django.shortcuts import render, redirect
from .models import Kullanicibilgileri, Words , CorrectAnswers
from django.urls import reverse  # URL için
from django.db import connection
from django.http import Http404
from django.db import IntegrityError  # Hata yönetimi için
from django.contrib.auth.hashers import make_password

import random ,datetime 
from dateutil.relativedelta import relativedelta




def userProfil(request):
    number_question = None
    #  önce oturumda bir kullanıcı var mı yok mu kontrol edelim
    user_id = request.session.get('user_id')

    if user_id:
        print('kullanıcı oturumu açık')
        print(user_id)

        user_info = Kullanicibilgileri.objects.get(user_id = user_id) 

        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM correct_answers where user_id = %s',[user_id])
        

            # Sonuçları alın ve bir listeye dönüştürün
            correct_answers = list(cursor.fetchall())

            # # print("sql sorgusu sonucu : ",rows)
            # # print(len(rows))
            # rows = list(rows)
            # print(type(rows))

            # for row in correct_answers:
            #     # Belirli indekslerdeki elemanları al
            #     true_word = row[2]  # üçüncü sütun (örnek: 'true_word')
            #     answer_date = row[3]  # dördüncü sütun (örnek: 'answer_date')

            #     print("True Word:", true_word, "Answer Date:", answer_date)

            context = {
                'user_info':user_info,
                'correct_answers': correct_answers,
            }

            number_question
            if request.method == "POST":
                form_type = request.POST.get('form_type', None)  # Gizli alanı kontrol edin

                if form_type == 'change_question_count':  # Soru sayısını değiştirme formu
                    number_question = request.POST.get('number_question', 10)  # Varsayılan 10
                    request.session['number_question'] = int(number_question)  # Oturumda kelime sayısını sakla
                    return redirect('wordPage', number_question=number_question)

                elif form_type == 'add_word':
                    # Yeni kelim ekleme formu
                    word = request.POST.get('word')
                    true_word = request.POST.get('true_word')
                    false_word1 = request.POST.get('false_word1')
                    false_word2 = request.POST.get('false_word2')
                    # kelimenin mevcut olup olmadığını kontrol edelim 
                    existing_word = Words.objects.filter(
                        word= word,
                        true_word=true_word,
                        false_word1=false_word1,
                        false_word2 = false_word2,
                    ).exists()

                    if existing_word:
                        context['message'] = 'bu kelime kelime havuzunda zaten mevcut'
                    else:
                        try:
                            # Kelimeyi eklemeyi deneyin
                            new_word = Words.objects.create(
                                word=word,
                                true_word=true_word,
                                false_word1=false_word1,
                                false_word2=false_word2
                            )
                            new_word.save()
                            context['message'] = "Kelime başarıyla eklendi"

                        except IntegrityError:
                            # Tekrarlanan giriş durumu için bir hata mesajı
                            context['message'] = "Bu kelime zaten var, farklı bir kelime deneyin"
                    return render(request, 'partials/user.html', context)


                    
    else:
        context = {'error' : 'Kullanıcı oturumu açık değil.' }
    return render(request,'partials/user.html',context)


def homePage(request):
    # Oturumda kullanıcıyı kontrol edin
    user_id = request.session.get('user_id')
    username = request.session.get('username')

    if user_id:
        context = {
            'kullanici': {'user_id': user_id, 'username': username}
        }
        default_number = 10

        # Oturum açıksa kullanıcı bilgileriyle render
        return redirect('wordPage',number_question =default_number)
    else:
        # Oturum yoksa giriş sayfasına yönlendirin
        return redirect('loginPage')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Kendi modelinizi kullanarak kullanıcıyı doğrulayın
        user = Kullanicibilgileri.objects.filter(
            username=username, user_password=password).first()

        if user:
            # Oturum başlatmak için session kullanın
            request.session['user_id'] = user.user_id
            request.session['username'] = user.username
            number_question = request.session.get('number_question',10) # varsayılan olarak 10 
            # Başarılı giriş sonrası ana sayfaya yönlendirin
            print(username,password)
            return redirect('wordPage',number_question=number_question)
        else:
            # Giriş başarısızsa hata mesajıyla tekrar giriş sayfasını render edin
            print(username,password)
            
            context = {'error': 'Kullanıcı adı veya parola yanlış'}
            return render(request, 'partials/login.html', context)
    
    # GET isteği için giriş sayfasını render edin
    return render(request, 'partials/login.html')  # Giriş için şablonu döndür
""
def registerPage(request):
    if request.method == 'POST':
        # POST verileri AL
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        username = request.POST.get('username')
        mail = request.POST.get('mail')
        password = request.POST.get('password')
        re_password = request.POST.get('re-password')

        # Boş Değer Kontorlü yapılsın

        if not (name and surname and username and password and password and re_password):
            return render(request, 'partials/register.html')

        user = Kullanicibilgileri.objects.create(
            name=name,
            surname=surname,
            username=username,
            user_mail=mail,
            user_password=password
        )

        user.save()
        return render(request, 'partials/login.html')

    return render(request, "partials/register.html")

def logOut(request):
    # global isLogin  # global değişkeni kullanacağımızı belirt

    # isLogin = False

    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('homePage')


def wordPage(request,number_question = None):
    try:
        number_question = int(number_question)  # Parametreyi integera dönüştür
        if number_question <= 0:
            raise ValueError("Soru sayısı sıfır veya negatif olamaz.")

    except ValueError:
        raise Http404("Geçersiz soru sayısı.")

    if number_question is None:
        number_question = request.session.get('number_question',10)
    else:
        # oturumdaki kelime sayısını güncelleyin
        request.session['number_question'] = int(number_question)


    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('loginPage')  # Kullanıcı kimliği yoksa yönlendirme

    # POST isteğinde kelimeleri tekrar oluşturmayı engelleyin
    
    if request.method == 'GET':
        bugun = datetime.date.today()
        # Kullanıcının doğru bildiği kelimeleri alalım
        correct_word_ids = CorrectAnswers.objects.filter(user_id=user_id).values_list('word_id', flat=True)

        # next_date alanı bugünkü tarihe eşit olan kelimelerin kimliklerini alalım
        correct_word_ids_today = CorrectAnswers.objects.filter(user_id = user_id , next_date=bugun).values_list('word_id', flat=True)
        
        print(type(correct_word_ids_today))

        # Doğru bildiği kelimeleri hariç tutarak rastgele seçilen 10 kelimeyi alın
        kelimeler = Words.objects.exclude(word_id__in=correct_word_ids).order_by('?')

        # Eğer next_date'i bugünkü tarihe eşit olan kelimeler varsa, onları da ekleyin
        if correct_word_ids_today:            
            kelimeler_today = Words.objects.filter(word_id__in=correct_word_ids_today)
            kelimeler = (kelimeler | kelimeler_today).distinct()

        # Son olarak, 10 kelime alın
        kelimeler = kelimeler[:number_question]

        # # Rastgele gelen kelimelerden doğru bildiklerini hariç tutarak 10 kelime alın
        # kelimeler = Words.objects.exclude(word_id__in=correct_word_ids).order_by('?')[:number_question]

        for kelime in kelimeler:
            mixed_words = [kelime.true_word, kelime.false_word1, kelime.false_word2]
            random.shuffle(mixed_words)
            kelime.random_words = mixed_words  # Rastgele karıştırılmış kelimeler
        
        # Kullanıcının doğru yanıtladığı kelimeleri güncelle
        update_next_date_and_correct_count(user_id)

    else:
        # POST durumunda, mevcut kelimeleri kullanın
        kelimeler = request.session.get('kelimeler', [])

    context = {
        'kelimeler': kelimeler,
        'kelime_sayisi':number_question
    }

    if request.method == 'POST':
        is_any_selected = any(
            key.startswith('kelime_') for key in request.POST.keys()
        )

        if not is_any_selected:  # Seçili radyo düğmesi yoksa
            print('herhangi bir kelime seçilmedi')

            context.update({
                'hata':'Hiçbir kelime seçmediniz. Lütfen en az bir kelime seçin.'
            })
            return render(request, 'partials/main.html', context)  # Hata mesajını döndür
        
        correct_answers = []
        
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue  # CSRF tokenını atlayın
            
            kelime_id = int(key.replace('kelime_', ''))
            kelime = Words.objects.get(word_id=kelime_id)  # Kelimeyi alın
            
            if value == kelime.true_word:
                correct_answers.append(kelime)  # Doğru kelimeler
            print(correct_answers)
         # Doğru cevapları veritabanına kaydet
        save_correct_answers(correct_answers, user_id)
        
        
        context.update({
            'correct_answers': correct_answers,
        })

    return render(request, 'partials/main.html', context)  # Şablonu render edin



def update_next_date_and_correct_count(user_id):

    """
        Kullanıcının doğru yanıtladığı kelimelerin next_date ve correct_count alanlarını günceller.
    """

    correct_answers = CorrectAnswers.objects.filter(user_id= user_id)
    
    bugun = datetime.date.today()

    bir_gun = datetime.timedelta(days=1)
    bir_hafta = datetime.timedelta(days=7)
    bir_ay=relativedelta(months=1)
    uc_ay = relativedelta(months=3)
    alti_ay = relativedelta(months=6)
    bir_sene = relativedelta(years=1)

    for answer in correct_answers:
        fark = answer.answer_date - bugun
        fark = fark.days
        fark = abs(fark)

        if(answer.correct_count == 1):

            if(fark == 0):
                answer.next_date = answer.answer_date + bir_gun
            elif(fark > 0):
                # eğer kullanıcı bir soruyu doğru yaptıktan 1 gün sonra tekrar giriş yapmamışsa o gün soru karşısına çıksın
                answer.next_date = bugun

        elif(answer.correct_count == 2):
            # print('doğru cevaplama sayısı 2',user_id)

            if(fark <= 7 ):
                answer.next_date = answer.answer_date + bir_hafta
            elif(fark > 7 ):
                # eğer kullanıcı soruyu iki defa doğru yanıtlamış ve ama gününde programa girip devam etmemiş ise hangi gün giriş yaptıysa o gün o soru karşısına çıksın
                answer.next_date = bugun
            
        elif(answer.correct_count == 3):

            if(fark <= 30):
                answer.next_date = answer.answer_date + bir_ay
            elif(fark > 30):
                answer.next_date = bugun                

        elif(answer.correct_count == 4):
            if(fark <= 90):
                answer.next_date = answer.answer_date + uc_ay

            elif(fark > 90):
                answer.next_date = bugun    
        
        elif(answer.correct_count == 5):
            if(fark <= 180):
                answer.next_date = answer.answer_date + alti_ay

            elif(fark > 180):
                answer.next_date = bugun   

        elif(answer.correct_count == 6):
            if(fark <= 365):
                answer.next_date = answer.answer_date + bir_sene

            elif(fark > 365):
                answer.next_date = bugun   

        answer.save()

    



def save_correct_answers(correct_answers, user_id):
    bugun = datetime.date.today()

    for true_word in correct_answers:
        word = Words.objects.get(word=true_word)

        correct_answer, created = CorrectAnswers.objects.get_or_create(
            word_id=word.word_id,
            user_id=user_id,
            defaults={'true_word': word.word, 'answer_date': bugun}
        )

        if created:
            # Eğer kayıt oluşturulduysa, yani kullanıcı bu kelimeyi ilk kez doğru yanıtladıysa
            correct_answer.correct_count = 1  # Correct count değerini 1 olarak ayarla
        else:
            # Kayıt zaten varsa, yani kullanıcı bu kelimeyi daha önce doğru yanıtladıysa
            correct_answer.correct_count += 1  # Correct count değerini artır

        correct_answer.save()  # Değişiklikleri kaydet

def reset_password(request):
    context = {}

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        
        if form_type == "reset-password":
            username = request.POST.get('username')
            user_mail = request.POST.get('user_mail')
            new_password = request.POST.get('password')
            re_password = request.POST.get('re-password')

            # Kullanıcıyı doğrulama işlemi
            user = Kullanicibilgileri.objects.filter(username=username, user_mail=user_mail).first()

            if user:
                if new_password == re_password:
                    # Şifreleri eşleştirin ve hash'leyin
                    user.user_password = new_password   # Güncelle
                    user.save()  # Değişiklikleri kaydedin
                    
                    context['message'] = "Şifre başarıyla sıfırlandı."
                else:
                    # Parolalar eşleşmezse mesaj verin
                    context['message'] = "Parolalar eşleşmiyor, lütfen tekrar deneyin."
            else:
                # Kullanıcı bulunamazsa mesaj verin
                context['message'] = "Kullanıcı adı ve/veya e-posta adresi bulunamadı."

    return render(request, 'partials/reset_password.html', context)