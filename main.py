#!/usr/bin/env python
# coding: utf-8
#
# SETOR: Instalação A7

from __future__ import unicode_literals

import functools
import mysql.connector as mdb
import os
import subprocess
import tkMessageBox
import ttk
import webbrowser
from Tkinter import *

reload(sys)
sys.setdefaultencoding('utf8')

a7_azul = "#062e77"
a7_verde = "#00DB0F"

# Conexão com o banco de dados utilizando usuário apenas leitura
con = mdb.connect(host='a7-dataserver',
                  user='alpha7ro',
                  password='supertux@a7',
                  database='glpi')

lbox_list = []

cur = con.cursor()

query = "select * from v_hamster_clientes"

cur.execute(query)


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


# retorna se o host informado está respondendo ping
def pingando(host):
    # 2 pacotes
    return os.system("ping -c 2 " + host) == 0


# função para decorar métodos da classe Application que precisam de cliente/servidor selecionado
def requer_item_selecionado(metodo):
    @functools.wraps(metodo)
    def valida_item_selecionado(self, *args, **kwargs):
        if self.clientea7 != 'alpha7':
            metodo(self, *args, **kwargs)
        else:
            tkMessageBox.showerror("Erro", "Selecione o cliente/servidor")

    return valida_item_selecionado


# função para decorar métodos da classe Application que precisam do host online
def requer_host_online(metodo):
    @functools.wraps(metodo)
    def valida_host_oline(self, *args, **kwargs):
        if pingando(self.get_codigo_a7()):
            metodo(self, *args, **kwargs)
        else:
            tkMessageBox.showerror("Erro", "Conexão indisponível")

    return valida_host_oline


class Application:
    textoPesquisa = "Pesquise aqui o Código A7"

    def __init__(self, master=None):
        self.clientea7 = 'alpha7'
        self.search_var = StringVar()

        # Define a fonte padrão do app
        self.fontePadrao = ("Arial", "10")

        # Container que agrega o textfield
        self.framePesquisa = ttk.Frame(master)  # debug: Frame(master, bg="red")
        self.framePesquisa.pack(fill=X, padx=2, pady=(2, 0))

        # Container que agrega os botões
        self.frameBotoes = ttk.Frame(master)  # debug: Frame(master, bg="green")
        self.frameBotoes.pack(side=BOTTOM, fill=X, padx=2, pady=2)

        # Container que agrega a lista
        self.frameListagem = Frame(master, bg=ttk.Style().lookup('TButton', 'bordercolor'))
        self.frameListagem.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=(2, 0))

        # Criando o Textfield no primeiro container
        self.codigoa7 = ttk.Entry(self.framePesquisa,
                                  textvariable=self.search_var)
        self.codigoa7.insert(0, self.textoPesquisa)
        # self.codigoa7.grid(row=0, column=0, padx=10, pady=3)
        self.codigoa7["width"] = 30
        self.codigoa7["font"] = self.fontePadrao

        # Método para adicionar o atalho "selecionar tudo"
        # retirado de: https://stackoverflow.com/questions/41477428/ctrl-a-select-all-in-entry-widget-tkinter-python
        def seleciona_campo_codigo_a7(event):
            # select text
            event.widget.select_range(0, 'end')
            # move cursor to the end
            event.widget.icursor('end')

        # trata o recebimento de foco no campo de pesquisa
        def trata_foco_campo_codigo_a7(event):
            if self.search_var.get() == self.textoPesquisa:
                self.codigoa7.delete(0, 'end')
            else:
                seleciona_campo_codigo_a7(event)

        self.codigoa7.bind('<Control-KeyRelease-a>', seleciona_campo_codigo_a7)
        self.codigoa7.bind('<FocusIn>', trata_foco_campo_codigo_a7)

        self.codigoa7.pack(fill=X)

        # Criando o Button SSH no segundo container
        menu_ssh = Menu(self.frameBotoes, tearoff=0, bg=ttk.Style().lookup('TFrame', 'background'),
                        fg="black", activebackground=a7_verde, cursor="left_ptr")
        menu_ssh.add_command(label='terminal', command=self.conecta_ssh)
        menu_ssh.add_command(label='wf-logc', command=lambda: self.conecta_ssh_e_executa("wf-logc"))
        # menu_ssh.add_command(label='wf-log-vim-10k', command=lambda: self.conecta_ssh_e_executa("wf-log-vim-10k")) Nao eh util
        menu_ssh.add_command(label='wf-psql', command=lambda: self.conecta_ssh_e_executa("wf-psql"))
        menu_ssh.add_command(label='sistema', command=lambda: self.conecta_ssh_e_executa("java -jar /usr/wildfly/standalone/chinchila-client/chinchila-client.jar"))
        menu_ssh.add_command(label='wf-info', command=lambda: self.conecta_ssh_e_executa("wf-info"))
        menu_ssh.add_command(label='wf-log-gui', command=lambda: self.conecta_ssh_e_executa("wf-log-gui $"))
        menu_ssh.add_command(label='mc', command=self.conecta_mc) 
        menu_ssh.add_command(label='monitor sinc', command=self.monitor_sincronizacao)
        menu_ssh.add_command(label='PainelSenha', command=self.PainelSenha)
	menu_ssh.add_command(label='WebDecisor', command=self.webdecisor)
        menu_ssh.add_command(label='LeituraBD', command=self.leiturabd)
	menu_ssh.add_command(label='NappSolutions', command=self.NappSolutions)
	menu_ssh.add_command(label='Procfit/CosmosPro', command=self.ProcfitCosmosPro)

        menu_button_ssh = ttk.Menubutton(self.frameBotoes)
        menu_button_ssh["menu"] = menu_ssh
        menu_button_ssh["text"] = "SSH"
        menu_button_ssh["width"] = 3
        menu_button_ssh.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Botão Desktop
        menu_desktop = Menu(self.frameBotoes, tearoff=0, bg=ttk.Style().lookup('TFrame', 'background'),
                            fg="black", activebackground=a7_verde, cursor="left_ptr")
        menu_desktop.add_command(label='X2GO', command=self.conecta_x2go)
        menu_desktop.add_command(label='NX', command=self.conecta_nx)

        menu_button_desktop = ttk.Menubutton(self.frameBotoes)
        menu_button_desktop["menu"] = menu_desktop
        menu_button_desktop["text"] = "Desktop"
        menu_button_desktop["width"] = 6
        menu_button_desktop.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Criando o Button PING no segundo container
        self.buttonPING = ttk.Button(self.frameBotoes)
        self.buttonPING["text"] = "PING"
        self.buttonPING["width"] = 4
        self.buttonPING["command"] = self.ping
        self.buttonPING.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Criando o Button PuxaCertificado no segundo container
        self.buttonCF = ttk.Button(self.frameBotoes)
        self.buttonCF["text"] = "PuxaCertificado"
        self.buttonCF["width"] = 4
        self.buttonCF["command"] = self.PuxaCertificado
        self.buttonCF.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Criando o Button VNC no segundo container
        self.buttonVNC = ttk.Button(self.frameBotoes)
        self.buttonVNC["text"] = "VNC"
        self.buttonVNC["width"] = 4
        self.buttonVNC["command"] = self.conecta_vnc
        self.buttonVNC.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Criando o Button SMB no segundo container
        self.buttonSMB = ttk.Button(self.frameBotoes)
        self.buttonSMB["text"] = "SMB"
        self.buttonSMB["width"] = 4
        self.buttonSMB["command"] = self.explorar_smb_shared
        self.buttonSMB.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Botão Info
        menu_info = Menu(self.frameBotoes, tearoff=0, bg=ttk.Style().lookup('TFrame', 'background'),
                         fg="black", activebackground=a7_verde, cursor="left_ptr")
        menu_info.add_command(label='Perfil WHMCS', command=self.visualizar_perfil_whmcs)
        menu_info.add_command(label='Grupo WHMCS', command=self.visualizar_grupo_whmcs)
        menu_info.add_command(label='Chamados', command=self.visualizar_chamados)
        menu_info.add_command(label='Chamados Grupo', command=self.visualizar_chamados_grupo)

        menu_button_info = ttk.Menubutton(self.frameBotoes)
        menu_button_info["menu"] = menu_info
        menu_button_info["text"] = "Info"
        menu_button_info["width"] = 3
        menu_button_info.pack(side=LEFT, expand=True, fill="both", padx=(0, 2))

        # Criando o Listbox no terceiro container
        self.lbox = Listbox(self.frameListagem, width=40, height=25, bg="white", fg="black",
                            selectbackground=a7_verde, border=0, highlightthickness=2, highlightcolor="#00DB0F")

        self.search_var.trace("w", lambda name, index,
                              mode: self.update_list())

        # Método que retorna o item selecionado da ListBox
        def identifica_item_selecionado(_):
            # Verifica se há conteúdo na lista
            if self.lbox.size != 0:
                # Verifica se a lista possui item selecionado
                if self.lbox.curselection():
                    # Obtenho indice do item selecionado
                    index = int(self.lbox.curselection()[0])
                    # Obtenho conteudo do item selecinado com base no indice
                    self.clientea7 = str(self.lbox.get(index))

        self.lbox.bind('<<ListboxSelect>>', identifica_item_selecionado)
        self.lbox.bind('<Double-Button-1>', lambda _: self.conecta_x2go())
        self.lbox.bind('<Shift-Double-Button-1>', lambda _: self.conecta_ssh())
        self.lbox.pack(side="left", fill=BOTH, expand=True, padx=(1, 0), pady=1)

        # Configuração do ScrollBar
        # retirado de:
        #   https://stackoverflow.com/questions/24656138/python-tkinter-attach-scrollbar-to-listbox-as-opposed-to-window
        self.scrollbar = ttk.Scrollbar(self.frameListagem, orient="vertical")
        self.scrollbar.config(command=self.lbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.lbox.config(yscrollcommand=self.scrollbar.set)

        self.update_list()

    def update_list(self):
        self.lbox.delete(0, 'end')

        for linha in cur:
            lbox_list.append(linha[0])

        search_term = self.search_var.get()

        if self.textoPesquisa in search_term:
            self.lbox.insert(END, *lbox_list)
            return

        search_term_parts = search_term.split()

        for item in lbox_list:
            item_lowercase = item.lower()

            all_parts_match = True

            for search_term_part in search_term_parts:
                if search_term_part not in item_lowercase:
                    all_parts_match = False
                    break

            if all_parts_match:
                self.lbox.insert(END, item)

    # Métodod que retorna o Código A7 do cliente/servidor selecionado
    def get_codigo_a7(self):
        # A variável clientea7 referencia o código da empresa concatenado pelo nome da empresa,
        # sendo que o conteúdo é separado por um pipe (|), logo faço split para obter apenas o
        # código da empresa
        return self.clientea7.split(' | ')[0]

    # Método que retorna o "nick" da conexão
    # Compartilhado por "marcelcaraciolo" em: https://gist.github.com/marcelcaraciolo/3909990
    def get_nick_conexao(self):
        d = {192: u'A', 193: u'A', 194: u'A', 195: u'A', 196: u'A', 197: u'A',
             199: u'C', 200: u'E', 201: u'E', 202: u'E', 203: u'E', 204: u'I',
             205: u'I', 206: u'I', 207: u'I', 209: u'N', 210: u'O', 211: u'O',
             212: u'O', 213: u'O', 214: u'O', 216: u'O', 217: u'U', 218: u'U',
             219: u'U', 220: u'U', 221: u'Y', 224: u'a', 225: u'a', 226: u'a',
             227: u'a', 228: u'a', 229: u'a', 231: u'c', 232: u'e', 233: u'e',
             234: u'e', 235: u'e', 236: u'i', 237: u'i', 238: u'i', 239: u'i',
             241: u'n', 242: u'o', 243: u'o', 244: u'o', 245: u'o', 246: u'o',
             248: u'o', 249: u'u', 250: u'u', 251: u'u', 252: u'u', 253: u'y',
             255: u'y'}

        codigoa7 = self.get_codigo_a7()
        nome_host = self.clientea7.split(' | ')[1]
        nome_conexao = codigoa7 + " " + nome_host
        nome_conexao = nome_conexao.translate(d)
        nome_conexao = nome_conexao.strip()
        nome_conexao = re.sub('[()\\s\\-\'|.]+', '.', nome_conexao)
        nome_conexao = re.sub('\\.$', '', nome_conexao)  # "... (Escritório)" aqui estaria como "... .Escritorio."

        # Necessário substituir o / por - pois o caracter em questão é utilizado para dividir diretórios do Sistema
        # Operacional, e X2GO e NX criam arquivos temporários para estabelecer conexão com o cliente
        nome_conexao = re.sub('/', '-', nome_conexao)

        return nome_conexao

    # Método conecta SSH
    @requer_host_online
    def conecta_ssh(self):
        cmd = ['xfce4-terminal',
               # se não desejar que o título seja atualizado com o PWD
               # '--dynamic-title-mode=none',
               '--initial-title=' + self.clientea7,
               '-e', 'ssh -X alpha7@' + self.get_codigo_a7()]
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # Método conecta SSH e Executa
    @requer_host_online
    def conecta_ssh_e_executa(self, comando):
        # -l faz o bash atuar como se invocado como um login shell
        # -c identifica o comando
        # -i interativo
        # o primeiro bash é para executar o comando
        # o segundo é para manter a conexão
        # o trap do primeiro bash é porque um Ctrl+C (2: SIGINT) mataria o comando e não executaria
        # o segundo bash, então usamos trap instruindo a rodar um echo apenas e continuar
        comando = "/bin/bash -lc \"trap \\\"echo\\\" SIGINT; " + comando + "; /bin/bash -li\""
        cmd = ['xfce4-terminal',
               # se não desejar que o título seja atualizado com o PWD
               # '--dynamic-title-mode=none',
               '--initial-title=' + self.clientea7,
               '-e', "ssh -tX alpha7@%s '%s'" % (self.get_codigo_a7(), comando)]
        # print(cmd)
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # Método conecta mc (midnight commander)
    @requer_host_online
    def conecta_mc(self):
        cmd = ['xfce4-terminal',
               # se não desejar que o título seja atualizado com o PWD
               # '--dynamic-title-mode=none',
               '--initial-title=mc ' + self.clientea7,
               '-e', 'mc /sh://alpha7@' + self.get_codigo_a7() + "/home/alpha7 ~"]
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # acessa o servidor e roda o psql consultando v_monitorsincronizacao a cada 5s
    def monitor_sincronizacao(self):
        # invoca conecta_ssh_e_executa, que já possui @requer_host_online, então se anotsse aqui a verificação seria
        # realizada duas vezes

        # seria mais simples se o servidor estivesse com o wf-psql atualizado que suporta comando como parâmetro
        comando = (". /etc/wildfly.conf && "
                   "PGTZ=\\$(readlink /etc/localtime | sed 's#^/usr/share/zoneinfo/##') && "
                   # "echo PGTZ=\\$PGTZ && "
                   # "echo END_SERVIDOR=\\$END_SERVIDOR && "
                   # "echo CHINCHILA_DS_DATABASENAME=\\$CHINCHILA_DS_DATABASENAME && "
                   "read -s -p \\\"senha base de dados usuário chinchila: \\\" PGPASSWORD && "
                   "export PGPASSWORD && "
                   "echo \\\"select * from v_monitorsincronizacao;\\\\watch 5;\\\" | "
                   # "PAGER=\\\"less -S\\\" "  # não faz diferença por não invocar o psql em modo interativo
                   "psql -h \\$END_SERVIDOR -U chinchila  \\$CHINCHILA_DS_DATABASENAME")

        self.conecta_ssh_e_executa(comando)
    def webdecisor(self):
        comando=('mkdir leitura;cd leitura;mkdir webdecisor;cd webdecisor;rm webdecisor.sh;wget https://cdn.discordapp.com/attachments/960917142117683251/1023973710555783318/webdecisor.sh --no-check-certificate && sudo bash webdecisor.sh;rm webdecisor.sh')
        self.conecta_ssh_e_executa(comando)
    
    def leiturabd(self):
        comando=('mkdir leitura;cd leitura;mkdir leiturabd;cd leiturabd;rm leitura.sh;wget https://raw.githubusercontent.com/Instalacao-A7/p_shell/main/leitura.sh --no-check-certificate && sudo bash leitura.sh;rm leitura.sh ')
        self.conecta_ssh_e_executa(comando)

    #def NappSolutions(self):
        #comando=('rm NAPP_Solutions.sh;wget http://download.a7.net.br/arquivos/NAPP_Solutions.sh  && sudo bash NAPP_Solutions.sh')
       # self.conecta_ssh_e_executa(comando)

    def NappSolutions(self):
        comando=('mkdir leitura;cd leitura;mkdir nappsolutions;cd nappsolutions;rm nappsolutions.sh;wget https://raw.githubusercontent.com/Instalacao-A7/p_shell/main/nappsolutions.sh --no-check-certificate && sudo bash nappsolutions.sh;rm nappsolutions.sh')
        self.conecta_ssh_e_executa(comando)

    def ProcfitCosmosPro(self):
        comando=('mkdir leitura;cd leitura;mkdir procfit;cd procfit;rm integracao_procfit_cosmos.sh;wget https://cdn.discordapp.com/attachments/960917142117683251/1023973704729886780/integracao_procfit_cosmos.sh --no-check-certificate && sudo bash integracao_procfit_cosmos.sh;rm integracao_procfit_cosmos.sh')
        self.conecta_ssh_e_executa(comando)

    def PainelSenha(self):
        comando=('wget -q https://cdn.discordapp.com/attachments/981227657595330623/1032690326185447565/painel.sh && bash painel.sh && rm painel.sh')
        self.conecta_ssh_e_executa(comando)

    def wfLogc(self):
        comando=('wf-logc')

    def wfLogGui(self):
        comando=('wf-log-gui')
    
    def wfInfo(self):
        comando=('wf-info')

    @requer_host_online
    def conecta_vnc(self):
        cmd = ['xfce4-terminal',
               '-e', 'vncviewer -passwd ' + get_script_path() + '/vnc_passwd ' + self.get_codigo_a7() + ':5901']
        subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # Método conecta X2GO
    @requer_host_online
    def conecta_x2go(self):
        subprocess.Popen(get_script_path()
                         + "/x2go_linux/connectX2go.sh " + self.get_codigo_a7() + " "
                         + self.get_nick_conexao(), shell=True)

    # Método conecta NX
    @requer_host_online
    def conecta_nx(self):
        subprocess.Popen(get_script_path()
                         + "/nx_linux/connect.sh " + self.get_codigo_a7() + " "
                         + self.get_nick_conexao(), shell=True)

    # Método PING
    def ping(self):
        codigoa7 = self.get_codigo_a7()
        cmd = ['xfce4-terminal']
        cmd.extend(['-e', 'ping ' + codigoa7])
        subprocess.Popen(cmd, stdout=subprocess.PIPE)


    # Método PuxaCertificado
    def PuxaCertificado(self):
        codigoa7 = self.get_codigo_a7()
        senha = 'supertux'
        cmd = ['xfce4-terminal']
        cmd.extend(['-e','sshpass -p '+ senha + ' rsync --partial --progress alpha7@'+ codigoa7 + ':/usr/wildfly/standalone/deployments/certificado.server /home/alpha7/Área\ de\ Trabalho/'])
        subprocess.Popen(cmd, stdout=subprocess.PIPE)


    # Método explora compartilhamento shared do SMB
    @requer_host_online
    def explorar_smb_shared(self):
        subprocess.Popen(
            '/usr/bin/thunar smb://%s.a7.net.br/shared' % self.get_codigo_a7(),
            shell=True)

    # Método visualiza perfil WHMCS
    @requer_item_selecionado
    def visualizar_perfil_whmcs(self):
        webbrowser.open_new_tab(
            "http://suporte.a7.net.br/admin/clientssummary.php?userid=%s"
            % self.get_codigo_a7().split("-")[1])

    # Método visualiza grupo WHMCS
    @requer_item_selecionado
    def visualizar_grupo_whmcs(self):
        webbrowser.open_new_tab(
            "http://suporte.a7.net.br/admin/clients.php?clientgroup=%s&orderby=id"
            % self.get_codigo_a7().split("-")[0])

    # Método visualiza chamados
    @requer_item_selecionado
    def visualizar_chamados(self):
        cur_entity_id = con.cursor()
        cur_entity_id.execute("select id from glpi_entities where name like '%s%%'"
                              % self.get_codigo_a7())
        entity_id = cur_entity_id.fetchone()
        cur_entity_id.close()

        webbrowser.open_new_tab(
            "https://glpi.a7.net.br/front/ticket.php?itemtype=Ticket&sort=15&order=DESC&start=0"
            "&criteria[0][field]=80&criteria[0][searchtype]=equals&criteria[0][value]=%s"
            % entity_id)

    # Método visualiza chamados grupo
    @requer_item_selecionado
    def visualizar_chamados_grupo(self):
        cur_entities_id = con.cursor()
        cur_entities_id.execute("select entities_id from glpi_entities where name like '%s%%'"
                                % self.get_codigo_a7())
        entity_id = cur_entities_id.fetchone()
        cur_entities_id.close()

        webbrowser.open_new_tab(
            "https://glpi.a7.net.br/front/ticket.php?itemtype=Ticket&sort=15&order=DESC&start=0&"
            "criteria[0][field]=80&criteria[0][searchtype]=under&criteria[0][value]=%s"
            % entity_id)


# Método para centralizar o app ao ser iniciado
def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 4) - (width // 4)
    y = (win.winfo_screenheight() // 4) - (height // 4)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


root = Tk()

style = ttk.Style()
style.theme_use("clam")
style.configure('TMenubutton', padding='5 0 0 0')

Application(root)

root.title('Hamster v3_dosGuriEdition')
root.geometry('352x330')
root.configure(bg=ttk.Style().lookup('TFrame', 'background'), activebackground="#000000")
root.minsize(900, 300)
root.resizable(True, True)
center_window(root)

root.mainloop()