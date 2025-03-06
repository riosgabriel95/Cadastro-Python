import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re

# Conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        senha TEXT NOT NULL)''')
    conn.commit()
    return conn

# Validação de email
def validar_email(email):
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(padrao, email)

# Validação de senhas
def validar_senha(senha):
    return len(senha) >= 6 and any(c.isdigit() for c in senha) and any(c.isalpha() for c in senha)

# Cadastro de usuário
def cadastrar_usuario():
    def salvar_usuario():
        nome = entry_nome.get()
        email = entry_email.get()
        senha = entry_senha.get()
        
        if not (nome and email and senha):
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios!")
            return
        if not validar_email(email):
            messagebox.showerror("Erro", "E-mail inválido!")
            return
        if not validar_senha(senha):
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres, incluindo letras e números!")
            return
        
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            cadastro_tela.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Este e-mail já está cadastrado!")
    
    cadastro_tela = tk.Toplevel()
    cadastro_tela.title("Cadastro de Usuário")
    cadastro_tela.geometry("300x300")
    
    tk.Label(cadastro_tela, text="Nome:").pack()
    entry_nome = tk.Entry(cadastro_tela)
    entry_nome.pack()
    
    tk.Label(cadastro_tela, text="E-mail:").pack()
    entry_email = tk.Entry(cadastro_tela)
    entry_email.pack()
    
    tk.Label(cadastro_tela, text="Senha:").pack()
    entry_senha = tk.Entry(cadastro_tela, show="*")
    entry_senha.pack()
    
    tk.Button(cadastro_tela, text="Cadastrar", command=salvar_usuario).pack(pady=10)

# Login de usuário
def login_usuario():
    email = entry_email.get()
    senha = entry_senha.get()
    
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario[1]}!")
    else:
        messagebox.showerror("Erro", "Credenciais inválidas!")

# Login do administrador
def login_admin():
    senha_admin = "admin123"  # Senha fixa para o administrador
    senha_digitada = entry_senha.get()
    if senha_digitada == senha_admin:
        abrir_gerenciador()
    else:
        messagebox.showerror("Erro", "Senha de administrador incorreta!")

# Gerenciador de usuários
def abrir_gerenciador():
    gerenciador = tk.Toplevel()
    gerenciador.title("Gerenciador de Usuários")
    gerenciador.geometry("500x500")
    
    def carregar_usuarios():
        for item in tree.get_children():
            tree.delete(item)
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email FROM usuarios")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
    
    def excluir_usuario():
        selecionado = tree.selection()
        if selecionado:
            user_id = tree.item(selecionado)['values'][0]
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            carregar_usuarios()
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
    
    def editar_usuario():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar!")
            return
        
        user_id, nome_atual, email_atual = tree.item(selecionado)['values']
        
        edit_tela = tk.Toplevel(gerenciador)
        edit_tela.title("Editar Usuário")
        edit_tela.geometry("300x250")
        
        tk.Label(edit_tela, text="Nome:").pack()
        entry_nome = tk.Entry(edit_tela)
        entry_nome.insert(0, nome_atual)
        entry_nome.pack()
        
        tk.Label(edit_tela, text="E-mail:").pack()
        entry_email = tk.Entry(edit_tela)
        entry_email.insert(0, email_atual)
        entry_email.pack()
        
        def salvar_edicao():
            novo_nome = entry_nome.get()
            novo_email = entry_email.get()
            
            if not (novo_nome and novo_email):
                messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
                return
            if not validar_email(novo_email):
                messagebox.showerror("Erro", "E-mail inválido!")
                return
            
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nome=?, email=? WHERE id=?", (novo_nome, novo_email, user_id))
            conn.commit()
            conn.close()
            carregar_usuarios()
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            edit_tela.destroy()
        
        tk.Button(edit_tela, text="Salvar", command=salvar_edicao).pack(pady=10)
    
    tree = ttk.Treeview(gerenciador, columns=("ID", "Nome", "Email"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Email", text="Email")
    tree.pack(pady=10)
    
    tk.Button(gerenciador, text="Editar Usuário", command=editar_usuario).pack(pady=5)
    tk.Button(gerenciador, text="Excluir Usuário", command=excluir_usuario).pack(pady=5)
    
    carregar_usuarios()

root = tk.Tk()
root.title("Sistema de Usuários")
root.geometry("300x300")

tk.Label(root, text="E-mail:").pack()
entry_email = tk.Entry(root)
entry_email.pack()

tk.Label(root, text="Senha:").pack()
entry_senha = tk.Entry(root, show="*")
entry_senha.pack()

tk.Button(root, text="Login Usuário", command=login_usuario).pack()
tk.Button(root, text="Criar Conta", command=cadastrar_usuario).pack()
tk.Button(root, text="Login Admin", command=login_admin).pack()

tk.Button(root, text="Sair", command=root.quit).pack()
root.mainloop()
