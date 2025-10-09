import i18n from 'i18next';
import {initReactI18next} from 'react-i18next';
import english from './assets/locales/en.json';
import french from './assets/locales/fr.json';

i18n.use(initReactI18next).init({
  resources: {
    en: {
      translation: english
    },
    fr: {
      translation: french
    }
  },
  lng: localStorage.getItem('language') || 'en',
  fallbackLng: 'en'
})

export default i18n;
