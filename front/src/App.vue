<template>
  <div id="app">
    <h1>Extrator de Tabelas PDF</h1>
    <input type="file" @change="handleFileUpload" />
    <div style="margin-top: 10px;">
      <button @click="uploadPDF">Extrair tabelas do PDF</button>
    </div>
    <div style="margin-top: 10px;">
      <button @click="unifyTables">Unificar as tabelas</button>
    </div>
    <div style="margin-top: 10px;">
      <button @click="importData">Importar</button>
    </div>
    <div style="margin-top: 10px;">
      <label>Empreendimento: </label>
      <input type="text" v-model="empreendimento" placeholder="Digite o nome do empreendimento" />
    </div>
    <div style="margin-top: 10px;color: orange;">
      <span>{{ this.resultado }}</span>
    </div>

    <div v-if="tables.length">
      <div v-for="(table, tableIndex) in tables" :key="tableIndex">
        <h2>Tabela {{ tableIndex + 1 }}</h2>        

        <div v-if="tableIndex === 0">
          <div v-for="index in table[0].length" :key="index">
            <label :for="'column-' + index">Selecione o campo <b>DePara</b> da coluna {{ index }}:</label>
            <select v-model="table[0][index - 1]" :id="'column-' + index">
              <option v-for="(field, fieldIndex) in dbFields" :key="fieldIndex" :value="field">
                {{ field }}
              </option>
            </select>
          </div>
        </div>

        <div style="margin-top: 10px;margin-bottom: 10px">
          <button @click="removeTable(tableIndex)">Excluir Tabela</button>
        </div>

        <table>
          <thead>
            <tr>
              <th v-for="(header, colIndex) in table[0]" :key="colIndex">
                {{ header }}
                <button @click="removeColumn(tableIndex, colIndex)">X</button>
              </th>
              <th>
                <button @click="removeRow(tableIndex, 0)">X</button>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in table.slice(1)" :key="rowIndex">
              <td v-for="(cell, colIndex) in row" :key="colIndex" contenteditable @input="editCell(tableIndex, rowIndex + 1, colIndex, $event)">
                {{ cell }}
              </td>
              <td>
                <button @click="removeRow(tableIndex, rowIndex + 1)">X</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      tables: [], // Lista de tabelas vindas do PDF
      dbFields: [
        "Unidade",
        "Area",
        "Valor",
        "Quartos",
        "Avaliacao",
        "Posicao",
        "Vagas"
      ],
      empreendimento: '',
      resultado: ''
    };
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    uploadPDF() {
      const formData = new FormData();
      formData.append('file', this.file);

      fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        this.tables = data.tables; // Recebe todas as tabelas do backend
        this.resultado = "Tabelas extraídas com sucesso"
      })
      .catch(error => {
        console.error("Erro ao fazer upload do PDF:", error);
        this.resultado = error
      });
    },
    editCell(tableIndex, rowIndex, colIndex, event) {
      this.tables[tableIndex][rowIndex][colIndex] = event.target.innerText
    },
    removeRow(tableIndex, rowIndex) {
      this.tables[tableIndex].splice(rowIndex, 1);
    },
    removeColumn(tableIndex, colIndex) {
      this.tables[tableIndex].forEach(row => row.splice(colIndex, 1));
    },
    removeTable(tableIndex) {
      this.tables.splice(tableIndex, 1);
    },
    unifyTables(){
      // Percorre todas as tabelas a partir de index 1 (tabelas 1, 2, ...)
      for (let i = 1; i < this.tables.length; i++) {
        // Adiciona as linhas de cada tabela subsequente em tables[0]
        this.tables[0] = this.tables[0].concat(this.tables[i].slice(1));  // .slice(1) para não adicionar o cabeçalho
      }
      
      // Remove as tabelas restantes após unificação
      this.tables = [this.tables[0]];

      this.resultado = "Tabelas unificadas com sucesso";
    },
    importData() {
      if (this.tables.length > 1) {
        this.resultado = "Envie apenas uma tabela com os dados tratados. Use o botão Unificar tabelas quando todas estiverem com as mesmas colunas equivalentes.";
        return;
      }

      var data = {
        empreendimento: this.empreendimento,
        dados: this.tables[0]
      }

      fetch('http://localhost:5000/importar', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
          }
      })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
        this.resultado = data.message;
      })
      .catch(error => {
        console.error("Erro ao importar os dados da tabela: ", error.message);
        this.resultado = "Erro ao importar os dados da tabela: " + data.message;
      });
    }
  }
};
</script>

<style>
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}
table, th, td {
  border: 1px solid black;
}
th, td {
  padding: 8px;
  text-align: center;
}
</style>
