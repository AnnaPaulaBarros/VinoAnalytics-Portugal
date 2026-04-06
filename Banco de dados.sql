-- Projeto: VinoAnalytics Portugal
-- Objetivo: Estruturação e análise da produção vinícola.
-- Autor: Anna Paula Barros da Silva.

-- 1. Criar banco de dados (idempotente)
-- Aqui verifiquei se o banco de dados já existe antes de criar.
-- Isso evita erro caso o script seja executado mais de uma vez.
IF NOT EXISTS (
    SELECT 1 FROM sys.databases 
    WHERE name = 'VinoAnalytics_Portugal'
)
BEGIN
    -- Caso o banco não exista, ele será criado com este comando.
    CREATE DATABASE VinoAnalytics_Portugal;
END
GO
-- O GO separa os blocos de execução no SQL Server.

-- Define que todos os próximos comandos serão executados dentro deste banco.
USE VinoAnalytics_Portugal;
GO

-- 2. Criar tabela.
-- Verifica se a tabela já existe no banco de dados.
IF NOT EXISTS (
    SELECT 1 
    FROM sys.objects 
    WHERE object_id = OBJECT_ID(N'dbo.Producao_Vinho') 
    AND type = 'U' -- 'U' significa User Table (tabela criada pelo usuário)
)
BEGIN
    -- Cria a tabela que armazenará os dados da produção vinícola.
    CREATE TABLE Producao_Vinho (
        -- ID único da região.
        -- PRIMARY KEY garante que não haverá duplicidade e cria um índice automaticamente.
        ID_Regiao INT PRIMARY KEY,
        -- Nome da região vinícola.
        -- VARCHAR(100) permite armazenar texto com até 100 caracteres.
        -- NOT NULL garante que o campo não pode ficar vazio.
        Nome_Regiao VARCHAR(100) NOT NULL,
        -- Ano da safra.
        -- Permite analisar outros anos.
        Ano INT NOT NULL,
        -- Quantidade produzida em hectolitros.
        -- BIGINT é utilizado para suportar grandes volumes de dados.
        Quantidade_HL BIGINT NOT NULL
    );
END
GO

-- 3. Limpar dados (para evitar duplicidade)
-- Verifica se a tabela existe antes de executar.
IF OBJECT_ID('dbo.Producao_Vinho', 'U') IS NOT NULL
BEGIN
    -- Remove todos os dados da tabela.
    -- Diferente do DELETE, o TRUNCATE é mais performático e reseta o armazenamento.
    TRUNCATE TABLE Producao_Vinho;
END
GO

-- 4. Inserção dos dados
-- Utiliza comando DML (Data Manipulation Language) para inserir registros na tabela.
INSERT INTO Producao_Vinho (ID_Regiao, Nome_Regiao, Ano, Quantidade_HL)
VALUES 
-- Cada linha representa uma região vinícola de Portugal.
-- Os valores são inseridos na ordem das colunas definidas.
(1, 'Entre Douro e Minho', 2025, 1005345),
-- Região com produção superior a 1 milhão de hectolitros.
(2, 'Trás-os-Montes', 2025, 1240619),
-- Segunda maior produção entre as regiões analisadas.
(3, 'Beira Litoral', 2025, 351759),
-- Produção intermediária.
(4, 'Beira Interior', 2025, 270771),
-- Produção menor comparada às regiões líderes.
(5, 'Ribatejo e Oeste', 2025, 2131394),
-- Maior produtora de vinho no conjunto de dados.
(6, 'Alentejo', 2025, 901003),
-- Região tradicional com produção relevante.
(7, 'Algarve', 2025, 16758),
-- Produção relativamente baixa.
(8, 'Açores', 2025, 11538),
-- Produção insular com menor escala.
(9, 'Madeira', 2025, 26977);
-- Região insular conhecida por vinhos específicos.
GO

-- 5. Consulta base
-- Seleciona todos os dados da tabela para análise.
SELECT * 
FROM Producao_Vinho
-- Ordena os resultados do maior para o menor volume de produção.
-- Isso facilita identificar rapidamente as regiões líderes (outliers positivos).
ORDER BY Quantidade_HL DESC;