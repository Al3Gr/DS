using Client.Exceptions;
using Client.Models;
using Client.Services;
using Microsoft.Maui.Storage;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace Client.Views.ViewModels
{
    public class PostsViewModel : INotifyPropertyChanged
    {

        private Page pageBinded;
        private string queryTag;
        private int pageNumber;

        //l'observableCollection notifica in automatico nel caso di aggiunta/rimozione di post
        private ObservableCollection<PhotoInfoModel> posts;
        private bool isLoading;
        private string searchQuery;

        public ObservableCollection<PhotoInfoModel> Posts
        {
            get => posts;
            set
            {
                posts = value;
                NotifyPropertyChanged(nameof(Posts));
            }
        }

        //proprietà per indicare che la finestra sta caricando
        public bool IsLoading
        {
            get => isLoading;
            set
            {
                isLoading = value;
                NotifyPropertyChanged(nameof(IsLoading));
                NotifyPropertyChanged(nameof(IsNotLoading));
            }
        }

        public bool IsNotLoading
        {
            get => !isLoading;
        }

        //proprietà che rappresenta la query cercata dal cliente
        public string SearchQuery
        {
            get => searchQuery;
            set
            {
                searchQuery = value;
                NotifyPropertyChanged(nameof(SearchQuery));
            }
        }

        public ICommand Search { get; set; }
        public ICommand SearchMore { get; set; }

        public PostsViewModel(Page pageBinded, string queryTag)
        {
            this.pageBinded = pageBinded;
            this.queryTag = queryTag;
            SearchQuery = queryTag;
            pageNumber = 0;

            Search = new Command(SearchClicked);
            SearchMore = new Command(SearchMoreHandler);

            DownloadPost(0);
        }

        private async void DownloadPost(int skip)
        {
            IsLoading = true;

            try
            {
                var lista = await RestService.Instance.GetPosts(queryTag, skip);
                if (skip == 0)
                    Posts = new ObservableCollection<PhotoInfoModel>(lista);
                else //ho cliccato more...
                    foreach (var post in lista)
                        Posts.Add(post);
            }
            catch (RestServiceException)
            {
                await App.Current.MainPage.DisplayAlert("Attenzione!", "Qualcosa è andato storto!", "Ok");
            }

            IsLoading = false;
        }

        public event PropertyChangedEventHandler PropertyChanged;

        //metodo per notificare gli observer che osservano l'evento PropertyChanged
        private void NotifyPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

        private void SearchClicked()
        {
            //se è uguale al precedente non cambio nulla
            if (SearchQuery == queryTag)
                return;
            if (string.IsNullOrEmpty(SearchQuery))
            {
                pageBinded.BindingContext = new PostsViewModel(pageBinded, "");
                return;
            }
            //trovo il tag che metcha la richiesta dell'utente
            string tag = ImagenetService.Instance.FindTag(SearchQuery);
            if (string.IsNullOrEmpty(tag))
            {
                App.Current.MainPage.DisplayAlert("Attenzione!", "Tag inesistente!", "Ok");
                return;
            }
            //ricarico il contenuto della pagina con le nuove informazioni
            pageBinded.BindingContext = new PostsViewModel(pageBinded, tag);
        }

        private void SearchMoreHandler()
        {
            //scarico i nuovi post, ogni get restituisce gli ultimi dieci risultati quindi lo skip è di 10
            DownloadPost((++pageNumber) * 10);
        }

        //utilizzato per refreshare tutta la pagina con gli ultimi contenuti più attuali
        public void Refresh()
        {
            pageBinded.BindingContext = new PostsViewModel(pageBinded, queryTag);
        }

    }
}
