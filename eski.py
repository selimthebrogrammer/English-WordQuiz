
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
        # Kullanıcının doğru bildiği kelimeleri alalım
        correct_word_ids = CorrectAnswers.objects.filter(user_id=user_id).values_list('word_id', flat=True)

        # Rastgele gelen kelimelerden doğru bildiklerini hariç tutarak 10 kelime alın
        kelimeler = Words.objects.exclude(word_id__in=correct_word_ids).order_by('?')[:number_question]





        for kelime in kelimeler:
            mixed_words = [kelime.true_word, kelime.false_word1, kelime.false_word2]
            random.shuffle(mixed_words)
            kelime.random_words = mixed_words  # Rastgele karıştırılmış kelimeler
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
