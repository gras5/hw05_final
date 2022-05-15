from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm

PASSWORD_ACTIONS_TEMPLATE = 'users/password_change.html'


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class UserPasswordChange(PasswordChangeView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Изменение пароля'
        context['card_header_text'] = 'Изменить пароль'
        context['button_text'] = 'Изменить пароль'
        return context


class UserPasswordChangeDone(PasswordChangeDoneView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Пароль изменён'
        context['card_header_text'] = 'Пароль изменён'
        context['notification_text'] = 'Пароль изменён успешно'
        return context


class UserPasswordReset(PasswordResetView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Сброс пароля'
        context['card_header_text'] = (
            'Чтобы сбросить старый пароль — введите адрес электронной почты, '
            'под которым вы регистрировались'
        )
        context['button_text'] = 'Изменить пароль'
        return context


class UserPasswordResetDone(PasswordResetDoneView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Сброс пароля прошёл успешно'
        context['card_header_text'] = 'Отправлено письмо'
        context['notification_text'] = (
            'Проверьте свою почту, вам должно прийти письмо '
            'со ссылкой для восстановления пароля'
        )
        return context


class UserPasswordResetConfirm(PasswordResetConfirmView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Новый пароль'

        if(context['validlink']):
            context['card_header_text'] = 'Введите новый пароль'
            context['button_text'] = 'Назначить новый пароль'
        else:
            context['card_header_text'] = 'Ошибка'
            context['notification_text'] = (
                'Ссылка сброса пароля содержит ошибку или устарела.'
            )
        return context


class UserPasswordResetComplete(PasswordResetCompleteView):
    template_name = PASSWORD_ACTIONS_TEMPLATE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Сброс пароля прошёл успешно'
        context['card_header_text'] = 'Отправлено письмо'
        context['notification_text'] = (
            'Ваш пароль был сохранен. Используйте его для входа'
        )
        return context
