<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Rastrear Pedido - Farmácia Online Isaías Muchamuene</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Rastrear Pedido</h1>
    <p>ID do Pedido: {{ pedido['id'] }}</p>
    <p>Status: Em preparação</p>  <!-- Simulação de rastreamento -->
    <a href="/historico">Voltar para Histórico</a>
</body>
</html>
