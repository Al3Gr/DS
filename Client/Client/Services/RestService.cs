using Client.Exceptions;
using Client.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;

using System.Threading.Tasks;

namespace Client.Services
{
    public class RestService
    {
        private static RestService _instance;
        private static object _instanceLock = new object();
        public static RestService Instance
        {
            get
            {
                lock (_instanceLock)
                {
                    if (_instance == null)
                        _instance = new RestService();
                    return _instance;
                }
            }
        }

        public const string urlServer = "http://localhost:80/";

        private readonly HttpClient _client;

        private RestService()
        {
            _client = new HttpClient()
            {
                MaxResponseContentBufferSize = 10 * 1024 * 1024
            };
        }

        public async Task<bool> Login(string username, string password)
        {
            HttpResponseMessage risposta = await TalkWithServerJson(HttpMethod.Post, urlServer + "users/login", new UserModel
            {
                username = username,
                password = password
            });
            if (risposta.IsSuccessStatusCode)
            {
                //se il login ha successo salvo il token
                UserService.Instance.Token = await risposta.Content.ReadAsStringAsync();
                return true;
            }
            else
                return false;
        }

        public async Task<bool> Signup(string username, string password)
        {
            HttpResponseMessage risposta = await TalkWithServerJson(HttpMethod.Post, urlServer + "users/signup", new UserModel
            {
                username = username,
                password = password
            });
            if (risposta.IsSuccessStatusCode)
            {
                //se il signup ha successo salvo il token
                UserService.Instance.Token = await risposta.Content.ReadAsStringAsync();
                return true;
            }
            else
                return false;
        }

        public async Task<bool> UploadImage(string description, byte[] image)
        {
            using (var content = new MultipartFormDataContent())
            {
                content.Add(new StringContent(description), "description");
                content.Add(new ByteArrayContent(image, 0, image.Length), "image", "files");
                
                HttpResponseMessage risposta = await TalkWithServerMultiPartFormData(HttpMethod.Post, urlServer + "photos/upload", content);

                if (risposta.IsSuccessStatusCode)
                    return true;
                else
                    return false;
            }
        }

        public async Task<List<PhotoInfoModel>> GetPosts(string query, int skip)
        {
            //creo l'endpoint corretto
            string endpoint = "get_photo?";
            if (!string.IsNullOrEmpty(query))
                endpoint += "tag=" + query + "&";
            if (skip > 0)
                endpoint += "skip=" + skip;

            HttpResponseMessage risposta = await TalkWithServer(HttpMethod.Get, urlServer + "photos/" + endpoint);

            if (risposta.IsSuccessStatusCode)
            {
                //resituisco la lista di post scaricati
                var stringa = await risposta.Content.ReadAsStringAsync();
                return Utility.DeserializeJSON<List<PhotoInfoModel>>(stringa);
            }
            else
                throw new RestServiceException(risposta);
        }

        // --------------- Talk with server ---------------
        private async Task<HttpResponseMessage> TalkWithServer(HttpMethod httpVerb, string url) => await TalkWithServerFinally(httpVerb, url, null);
        private async Task<HttpResponseMessage> TalkWithServerJson(HttpMethod httpVerb, string url, object request) => await TalkWithServerFinally(httpVerb, url, Utility.SerializeJSON(request));

        private async Task<HttpResponseMessage> TalkWithServerFinally(HttpMethod httpVerb, string url, string json)
        {
            try
            {
                //creo la richiesta
                HttpRequestMessage richiesta = new HttpRequestMessage
                {
                    Method = httpVerb,
                    RequestUri = new Uri(url),
                    Content = null
                };
                if (!string.IsNullOrEmpty(UserService.Instance.Token))
                    richiesta.Headers.Add("Authorization", UserService.Instance.Token); //aggiungo l'eventuale token, se disponibile
                if (!string.IsNullOrEmpty(json))
                    richiesta.Content = new StringContent(json, Encoding.UTF8, "application/json"); //aggiungo l'eventuale contenuto

                HttpResponseMessage risposta = await _client.SendAsync(richiesta);

                return risposta;
            }
            catch (Exception e)
            {
                return new HttpResponseMessage(HttpStatusCode.BadRequest);
            }
        }

        private async Task<HttpResponseMessage> TalkWithServerMultiPartFormData(HttpMethod httpVerb, string url, MultipartFormDataContent content)
        {
            try
            { 
                //creo la richiesta
                HttpRequestMessage richiesta = new HttpRequestMessage
                {
                    Method = httpVerb,
                    RequestUri = new Uri(url),
                    Content = content
                };
                
                if (!string.IsNullOrEmpty(UserService.Instance.Token))
                    richiesta.Headers.Add("Authorization", UserService.Instance.Token); //aggiungo l'eventuale token, se disponibile
                
                HttpResponseMessage risposta = await _client.SendAsync(richiesta);

                return risposta;
            }
            catch (Exception e)
            {
                return new HttpResponseMessage(HttpStatusCode.BadRequest);
            }
        }



    }
}
