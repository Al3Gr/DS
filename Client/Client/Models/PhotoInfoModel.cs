using Client.Services;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Client.Models
{
    public class PhotoInfoModel : INotifyPropertyChanged
    {
        public ObjectID _id { get; set; }
        public string username { get; set; }
        public string description { get; set; }
        public string url { get; set; }

        //utilizzata dall'interfaccia grafica per visualizzare l'immagine dall'url
        public ImageSource Image
        {
            get
            {
                try
                {
                    return ImageSource.FromUri(new Uri(RestService.urlServer + "get/" + url));
                }
                catch (Exception)
                {
                    //nel caso in cui l'url non esista o generi errori visualizzo un'immagine di default
                    return ImageSource.FromFile("nofoto.png");
                }
            }
        }

        //utilizzata dall'interfaccia grafica per visualizzare la stringa con i tag collegati all'immagine
        public string TagsString
        {
            get
            {
                string output = "";
                if (!AdditionalData.ContainsKey("tags"))
                    return "Non ci sono tag!";

                output = AdditionalData["tags"].ToString();

                return output;
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        //metodo per notificare gli observer che osservano l'evento PropertyChanged
        private void NotifyPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }


        //metodo per evitare che il parsing del json dia errore a causa di proprietà in più date dal server
        [JsonExtensionData]
        public IDictionary<string, JToken> AdditionalData { get; set; }
    }

    public class ObjectID
    {
        [JsonProperty("$oid")]
        public string Id { get; set; }
    }
}
