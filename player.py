from imports import *

links_m3u = []
store=JsonStore("login.json")


#-------Login-------#
class Login(Screen):
    def erro(self, msg):
        MDDialog(title="Erro", text=msg).open()
       
    def user_submit(self):
        username=self.ids.user.text
        password=self.ids.password.text
        url=self.ids.url.text
        
        if not username or not password or not url:
            self.erro("Complete ALL inputs")
        else:
            if store.exists("m3u_link"):
                store.delete('m3u_link')
            
            store.put("user", username=username, password=password, url=url)
            self.manager.current = "home"
    

    def m3u_submit(self):
        self.m3u_input = MDTextField(hint_text="M3U URL",mode="rectangle")
        access_button = MDRaisedButton(text="Access",on_release=lambda i: self.m3u_access(self.m3u_input.text))
        self.dialog = MDDialog(title="Enter your M3U link",type="custom",content_cls=self.m3u_input,buttons=[access_button])
        self.dialog.open()

    def m3u_access(self,link):
        if not self.m3u_input.text:
            self.erro("Empty Link")
        else:
            if store.exists("user"):
                store.delete('user')
            
            store.put("m3u_link",url=link)
            self.dialog.dismiss()
            self.manager.current = "home"





#-------Home-------#
class Home(Screen):   
   def logout(self):
       if store.exists("user"):
           store.delete('user')
       else:
           store.delete('m3u_link')
       
       self.manager.current = "login"
   
   def nav_open(self):
       self.ids.nav_drawer.set_state("open")      
       if store.exists("user"):
        data=store.get('user') 
        self.ids.lh_lb1.text=f"Username:{ data['username']}"
        self.ids.lh_lb2.text=f"Password:{ data['password']}"
        self.ids.lh_lb3.text=f"URL:{ data['url']}"
       else:
           data=store.get('m3u_link')
           self.ids.lh_lb3.text=f"URL:{data['url']}"

   def erro(self, msg):
        MDDialog(title="Erro", text=msg).open()
   


   def on_enter(self):
    if store.exists("user") and links_m3u ==[]:
        data=store.get('user')
        headers={"User-Agent": "Mozilla/5.0"}
        params = {'username':data['username'],'password':data['password'],'type':'m3u_plus','output':'ts'}
        url=f"{data['url']}/get.php"
        self.link=requests.get(url,headers=headers,params=params)
        print(self.link)
    
    elif store.exists("m3u_link") and links_m3u ==[]:
        data=store.get('m3u_link')
        url = data['url']   
        self.link=requests.get(url,headers=headers)
    Clock.schedule_once(self.reqst)
    
   def reqst(self,dt):
            try:
                self.link.encoding = 'utf-8'
                if self.link.status_code == 200:
                    row = self.link.text.splitlines()
                    regex = re.compile(
                        r'#EXTINF:-1\s+'
                        r'(?:tvg-id="(?P<tvg_id>[^"]*)"\s*)?'
                        r'(?:tvg-name="(?P<tvg_name>[^"]*)"\s*)?'
                        r'(?:tvg-logo="(?P<tvg_logo>[^"]*)"\s*)?'
                        r'(?:group-title="(?P<group>[^"]*)"\s*)?,'
                        r'(?P<name>.*)')
                        
                    for i in range(len(row)):
                        match = regex.match(row[i])
                        if match:
                            info = match.groupdict()
                            if i + 1 < len(row):
                                info['url'] = row[i + 1].strip()
                            links_m3u.append(info)
                                                    
            except requests.exceptions.RequestException as e:
                self.erro(f"Problema na conexão:\n[{e}]")
                self.manager.current = "login"




#-------Page1-------#
class Page1(Screen):
    channels=[]

    def on_pre_enter(self): 
        ch_group =[]
        
        for x in links_m3u:
            if x['url'].endswith(('.m3u8','.ts')) :
                ch_group.append(x['group'])
                self.channels.append(x)
        
        for x in dict.fromkeys(ch_group):
            self.ids.category_list.add_widget(OneLineListItem(text=x,
                                                        theme_text_color="Custom",
                                                        text_color="white",
                                                        on_press=lambda i, txt=x: self.Channels_list(txt)))
        
    def Channels_list(self,gpr):
        self.ids.Channel_cat_lb.text=gpr
        ch_list=[]
        for x in self.channels:
            if x['group'] == gpr:
                ch_list.append(x)
        
        self.ids.channel_list.clear_widgets()
        for x in ch_list:
            layout = MDCard(orientation='vertical',
                                size_hint=(None, None),
                                height='210dp', width='130dp',
                                md_bg_color='001F54',
                                shadow_color='0A1128',
                                elevation=2,
                                padding=5,
                                spacing='10dp')

            btn = MDRaisedButton(text="Watch Now",
                                font_size='20dp',
                                padding='10dp',
                                pos_hint={'center_x': 0.5},
                                md_bg_color='green',
                                on_release=lambda i,x=x:self.display(x['tvg_name'],x['url'])
                                )

            label = MDLabel(text=(x['tvg_name']),
                            theme_text_color="Custom",
                            text_color="white",
                            halign="center",
                            valign="center")
            layout.add_widget(label)
            layout.add_widget(btn)
            self.ids.channel_list.add_widget(layout)

    def display(self,nme,lnk):
        self.ids.Ch_name_lb.text=nme
        self.current_link = lnk
        if hasattr(self, 'current_video_player'):
            self.current_video_player.unload()
            self.ids.ch_vd_display.remove_widget(self.current_video_player)

        
        ch_player = Video(source=lnk,
                          state='play',
                          allow_stretch=True,
                          keep_ratio=True,
                          size_hint=(1, 1),
                          pos_hint={"center_x": 0.5, "center_y": 0.5})
        
        self.current_video_player = ch_player
        self.ids.ch_vd_display.add_widget(ch_player)

    def back_home(self):
        self.manager.current ='home'
        if hasattr(self, 'current_video_player'):
            self.current_video_player.unload()
    
    def play_media(self):
        self.current_video_player.unload()
        player_screen = self.manager.get_screen('tv')
        player_screen.set_stream(self.current_link)
        self.manager.current = 'tv'




#-------Page2-------#
class Page2(Screen):
    
    def on_pre_enter(self):
        self.ids.category_list.clear_widgets()
        Clock.schedule_once(self.load_category)
   
    def load_category(self,dt):     
        mv_group = []
        self.movies=[]
        for x in links_m3u:
            if x['url'].endswith('.mp4'):
                if not re.search(r'[sS]\d+[eE]\d+', x['tvg_name']):
                    mv_group.append(x['group'])
                    self.movies.append(x)
        
        for x in dict.fromkeys(mv_group):
            self.ids.category_list.add_widget(OneLineListItem(text=x,
                                                             theme_text_color="Custom",
                                                             text_color="white",
                                                             on_press=lambda i,lst=x: self.cards_filter(lst)))
    
    current_page = 0
    items_per_page = 15
    
    
    def cards_filter(self, text):
        self.mv_name = []
        self.links_mv = []
        self.logo_mv = []
        for x in self.movies:
            if x['group']==text:
                self.mv_name.append(x['name'])
                self.links_mv.append(x['url'])
                self.logo_mv.append(x['tvg_logo'])

        self.ids.category_lb.text = text
        self.current_page = 0
        self.show_page()
    
    def show_page(self):
       start = self.current_page * self.items_per_page
       end = start + self.items_per_page
       self.ids.movies_list.clear_widgets()
       
       for x,y,z in zip(self.mv_name[start:end],self.logo_mv[start:end],self.links_mv[start:end]):
            
            layout = MDCard(orientation='vertical',
                                size_hint=(None, None),
                                height='210dp', width='130dp',
                                md_bg_color='034078',
                                padding=5,
                                spacing='10dp')

            btn = MDRaisedButton(text="Watch Now",
                                font_size='20dp',
                                padding='10dp',
                                pos_hint={'center_x': 0.5},
                                md_bg_color='green',
                                on_release=lambda i,nme=x ,lgo=y,lnk=z:self.display(lgo,nme,lnk))

            label = MDLabel(text=x,
                            theme_text_color="Custom",
                            text_color="white",
                            halign="center",
                            valign="center")

            
            layout.add_widget(label)
            layout.add_widget(btn)
            self.ids.movies_list.add_widget(layout)

    def change_page(self, direction):
        max_pages = (len(self.mv_name)- 1) // self.items_per_page
        self.current_page += direction
        if self.current_page < 0:
            self.current_page = 0
        elif self.current_page > max_pages:
            self.current_page = max_pages
        self.show_page()
    
    
    def search_mv(self):
        srch_name=[]
        srch_logo=[]
        srch_link=[]        
        
        for x in self.movies:
            if x['name'].lower().startswith(self.ids.entry_mv.text):
                srch_name.append(x['name'])
                srch_logo.append(x['tvg_logo'])
                srch_link.append(x['url'])
                self.ids.movies_list.clear_widgets()                
                for x,y,z in zip(srch_name,srch_logo,srch_link):
            
                    layout = MDCard(orientation='vertical',
                                        size_hint=(None, None),
                                        height='210dp', width='130dp',
                                        md_bg_color='034078',
                                        padding=5,
                                        spacing='10dp')

                    btn = MDRaisedButton(text="Watch Now",
                                        font_size='20dp',
                                        padding='10dp',
                                        pos_hint={'center_x': 0.5},
                                        md_bg_color='green',
                                        on_release=lambda i,nme=x ,lgo=y,lnk=z:self.display(lgo,nme,lnk))

                    label = MDLabel(text=x,
                                    theme_text_color="Custom",
                                    text_color="white",
                                    halign="center",
                                    valign="center")

                    
                    layout.add_widget(label)
                    layout.add_widget(btn)
                    self.ids.movies_list.add_widget(layout)

    def display(self,logo,name,link):
            self.current_link = link        
            rqst = requests.get(logo, headers={"User-Agent": "Mozilla/5.0"})
            if rqst.status_code==200:
                with open("logos/logo_movie.jpg", "wb") as f:
                    f.write(rqst.content)           
                self.ids.movie_logo.reload()
                self.ids.movie_logo.source = "logos/logo_movie.jpg"

            self.ids.movie_name.text=name

    def play_media(self):
        player_screen = self.manager.get_screen('plyr')
        player_screen.ids.video.source = self.current_link
        player_screen.ids.video.state = 'play'
        self.manager.current = 'plyr'


#-------Page3-------#
class Page3(Screen):
    items_per_page = 15
    current_page = 0
    
    series=[]
    
    def on_pre_enter(self):
        self.ids.series_category.clear_widgets()
        Clock.schedule_once(self.load_category)
   
    def load_category(self,dt):     
        sr_group = []
        
        for x in links_m3u:
            if x['url'].endswith('.mp4'):
                if re.search(r'[sS]\d+[eE]\d+',x['tvg_name']):
                    sr_group.append(x['group'])
                    self.series.append(x)
        
        for x in dict.fromkeys(sr_group):
            self.ids.series_category.add_widget(OneLineListItem(text=x,
                                                        theme_text_color="Custom",
                                                        text_color="white",
                                                        on_press=lambda i,lst=x: self.card_filter(lst))) 
    
    
    def card_filter(self, txt):
        sr_name = []
        self.filtered_names = []
        
        sr_name.clear()
        self.filtered_names.clear()
        for x in self.series:
            if x['group'] == txt:
                filter = re.sub(r'\s*[sS]\d+[eE]\d+','',x['name']).strip()
                sr_name.append(filter)
    
        self.filtered_names = list(dict.fromkeys(sr_name))
        self.ids.category_lb.text = txt
        self.current_page = 0
        self.show_page()
    
    def search_sr(self):
        text = self.ids.entry_sr.text.strip().lower()
        sr_name = []
        self.filtered_names = []
        
        sr_name.clear()
        self.filtered_names.clear()
        for x in self.series:
            filter = re.sub(r'\s*[sS]\d+[eE]\d+', '', x['tvg_name']).strip()
            if filter.lower().startswith(text):
                sr_name.append(filter)

        self.filtered_names = list(dict.fromkeys(sr_name))
        self.current_page = 0
        self.show_page()
    
    
    def show_page(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        self.ids.series_list.clear_widgets()
        
        for x in self.filtered_names[start:end]:
            layout = MDCard(orientation='vertical',
                            size_hint=(None, None),
                            height='210dp', width='130dp',
                            md_bg_color='034078',
                            padding=5,
                            spacing='10dp')

            btn = MDRaisedButton(text="Watch Now",
                                font_size='20dp',
                                padding='10dp',
                                pos_hint={'center_x': 0.5},
                                md_bg_color='green',
                                on_press=lambda i, nme=x:self.display(nme))

            label = MDLabel(text=x,
                            theme_text_color="Custom",
                            text_color="white",
                            halign="center",
                            valign="center")

            layout.add_widget(label)
            layout.add_widget(btn)
            self.ids.series_list.add_widget(layout)
    
    
    def display(self,name):
        seasons=[]
        self.ids.season_list.clear_widgets()
        self.ids.episode_list.clear_widgets()
        self.ids.card_bt.clear_widgets()
        self.ids.season_lb.text="season"
        self.ids.sr_name_lb.text=name
        seasons.clear()
        
        for x in self.series:
            filter = re.sub(r'\s*[sS]\d+[eE]\d+','',x['tvg_name']).strip()
            if name == filter:
                season_filter=re.sub(r'\s*[eE]\d+','',x['tvg_name']).strip()
                seasons.append(season_filter)
        

        seasons=list(dict.fromkeys(seasons))

        for x in seasons:
            filter=re.search(r'[sS]\d+',x)
            s00=filter.group(0)
            
            self.ids.season_list.add_widget(MDRaisedButton(text=f"Season {s00}",
                                                           size_hint=(1,1),
                                                           on_press=lambda i,txt=s00,txt2=x,:self.show_episodes(txt,txt2)))
    
    def show_episodes(self,season,name):
        self.ids.season_lb.text=f"Season {season}"
        eps_=[]
        eps_.clear()
        
        for x in self.series:
            filter=re.sub(r'\s*[eE]\d+','',x['tvg_name']).strip()
            if filter == name:
                eps_.append(x)
        self.ids.episode_list.clear_widgets()
        
        for x in eps_:
            filter=re.sub(r'[sS]\d+[eE]\d+','',x['tvg_name']).strip()[:20]
            filter_ep=re.search(r'[eE]\d+',x['tvg_name'])
            
            self.ids.episode_list.add_widget(OneLineListItem(text=(filter+filter_ep.group(0)),
                                                            theme_text_color="Custom",
                                                            text_color="white",
                                                            on_press=lambda i, logo=x['tvg_logo'], url=x['url'], ep=filter_ep.group(0): self.image_display(logo, url, ep)))

        
            
    
    def image_display(self,logo,media,ep):
        rqst = requests.get(logo, headers={"User-Agent": "Mozilla/5.0"})
        
        if rqst.status_code==200:
            with open("logos/logo_sr.jpg", "wb") as f:
                f.write(rqst.content)           
            self.ids.sr_logo.reload()
            self.ids.sr_logo.source = "logos/logo_sr.jpg"
        self.ids.card_bt.clear_widgets()
        self.ids.card_bt.add_widget(MDRaisedButton(text="Play Now",
                                                   size_hint=(1,0.35),
                                                   on_press=lambda i,lnk=media:self.play_media(lnk)))
        self.ids.episode_lb.text=f"Episode {ep}"
    
    
    def change_page(self,direction):
        max_pages = (len(self.filtered_names)- 1) // self.items_per_page
        self.current_page += direction
        if self.current_page < 0:
            self.current_page = 0
        elif self.current_page > max_pages:
            self.current_page = max_pages
        self.show_page()

    def play_media(self,lnk):
        player_screen = self.manager.get_screen('plyr')
        player_screen.ids.video.source = lnk
        player_screen.ids.video.state = 'play'
        self.manager.current = 'plyr'

        

        
    



#-------Media_player-------#
class Player(Screen):
    def back_stop(self):
        self.ids.video.state = 'stop'
        self.manager.current = 'home'


#-------TV_player-------#
class Tv_player(Screen):
    def set_stream(self, link):
        self.ids.video.source = link
        self.ids.video.state = 'play'
    def back_stop(self):
        self.ids.video.state='stop'
        self.manager.current = 'pg1'



class IPTV(MDApp):
    def build(self):
        Builder.load_file("win.kv")
        
        self.store = JsonStore("login.json")
        self.sm = ScreenManager()
        self.sm.add_widget(Login(name='login'))
        self.sm.add_widget(Home(name='home'))
        self.sm.add_widget(Page1(name='pg1'))
        self.sm.add_widget(Page2(name='pg2'))
        self.sm.add_widget(Page3(name='pg3'))
        self.sm.add_widget(Tv_player(name='tv'))
        self.sm.add_widget(Player(name='plyr'))
        self.lg_verify()
        return self.sm
    
    def lg_verify(self):
        if self.store.exists("user") or self.store.exists("m3u_link"):
            self.sm.current = "home"
        else:
            self.sm.current = "login"
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Window.set_icon('logos/logo.png')
IPTV().run()
    