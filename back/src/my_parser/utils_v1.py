import xlsxwriter
# from djpipango.core.mail import send_mail



def save_to_excel_file(output, max_offers, id, start_date, index_from, last_index):
    # t_date = datetime.datetime.now().strftime('%d%m%Y%s%M%h')

    with xlsxwriter.Workbook(f'media/output_files/{start_date}_outputfile.xlsx') as wb:
        headers = ['ID', 'Сайт', 'Артикул', 'Наименование', 'Брэнд']
        merged_headers = ['Самое дешевое предложение', '№1', '№2', '№3', '№4', '№5']
        properties = ['Рейтинг', 'Наличие', 'Срок, дней', 'Цена, руб.']
        align_center_format = wb.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        if index_from == 0:
            worksheet = wb.add_worksheet('Sheet1')
            # Отрисовка обычных ячеек заголовков
            for col, head in enumerate(headers):
                worksheet.merge_range(0, col, 1, col, head, align_center_format)

            iteration = 0
            # Отрисовка объедененных ячеек предложений
            for col in range(5, len(merged_headers) * 4 + 1, 4):
                worksheet.merge_range(0, col, 0, col + 3, merged_headers[iteration], align_center_format)
                iteration += 1
                # Отрисовка ячеек с полями предложений
                for col2, prop in enumerate(properties):
                    worksheet.write(1, col2 + col, prop, align_center_format)
        else: 
            worksheet = wb.get_worksheet_by_name('Sheet1')

        #Отрисовка выходных данных
        for row, item in enumerate(output):
            worksheet.write(int(index_from)+row + 2, 0, int(index_from)+row, align_center_format)
            worksheet.write(int(index_from)+row + 2, 1, item['Сайт'][0], align_center_format)
            worksheet.write(int(index_from)+row + 2, 2, item['Артикул'][0], align_center_format)
            worksheet.write(int(index_from)+row + 2, 3, item['Наименование'][0], align_center_format)
            worksheet.write(int(index_from)+row + 2, 4, item['Бренд'][0], align_center_format)
            # Самое дешевое предложение
            if 'Самое дешевое предложение' in item:
                worksheet.write(int(index_from)+row + 2, 5, item['Самое дешевое предложение'][0]['Рейтинг'], align_center_format)
                worksheet.write(int(index_from)+row + 2, 6, item['Самое дешевое предложение'][0]['Наличие'], align_center_format)
                worksheet.write(int(index_from)+row + 2, 7, item['Самое дешевое предложение'][0]['Срок, дней'], align_center_format)
                worksheet.write(int(index_from)+row + 2, 8, item['Самое дешевое предложение'][0]['Цена, руб.'], align_center_format)
            for i in range(max_offers+1):
                if f'№{i}' in item:
                    worksheet.write(int(index_from)+row + 2, 5+4*i, item[f'№{i}'][0]['Рейтинг'], align_center_format)
                    worksheet.write(int(index_from)+row + 2, 6+4*i, item[f'№{i}'][0]['Наличие'], align_center_format)
                    worksheet.write(int(index_from)+row + 2, 7+4*i, item[f'№{i}'][0]['Срок, дней'], align_center_format)
                    worksheet.write(int(index_from)+row + 2, 8+4*i, item[f'№{i}'][0]['Цена, руб.'], align_center_format)
            
    from src.my_parser.models import ParserTask
    from django.contrib.auth.models import User
    if index_from == 0:
        task = ParserTask.objects.get(id=id)
        task.output_file = f'output_files/{start_date}_outputfile.xlsx'
        task.save()

    if index_from == last_index:
        task = ParserTask.objects.get(id=id)
        task.status = 'done'
        task.save()
        admin = User.objects.all().first()
        sended = send_mail(
                'Информация об окончании работы парсера.', 
                f'Задача номер - {task.pk} выполнена.', 
                'parser@uitdep.ru', 
                [admin.email], 
                fail_silently=False
        )


