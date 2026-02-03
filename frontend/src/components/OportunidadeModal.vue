<template>
  <BaseModal
    :show="show"
    :title="isEdit ? 'Editar Oportunidade' : 'Nova Oportunidade'"
    size="xl"
    @close="$emit('close')"
    @confirm="handleSubmit"
    :loading="loading"
  >

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Coluna Principal (Formulário) -->
      <form @submit.prevent="handleSubmit" class="lg:col-span-2 space-y-8">
        
        <!-- 1. Identificação (Kommo Style) -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-gray-400 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-gray-300 mr-3"></span>
            Definição
          </h3>
          
          <div class="space-y-6">
            <!-- Row 1: Contato, Telefone e Fonte -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Contato Principal -->
                <div class="relative">
                  <label class="text-sm font-bold text-gray-700 mb-1.5 flex justify-between">
                    <span>Contato Principal <span class="text-red-500">*</span></span>
                    <button type="button" @click="showNovoContatoModal = true" class="text-primary-600 hover:text-primary-700 text-[10px] font-black uppercase tracking-wider">+ Novo</button>
                  </label>
                  
                  <div class="relative group">
                    <input 
                      v-model="searchContatoPrincipal" 
                      type="text" 
                      class="input pr-16" 
                      placeholder="Buscar ou criar contato..."
                      @focus="showContatosPrincipalDropdown = true"
                    >
                    <div class="absolute inset-y-0 right-0 pr-10 flex items-center pointer-events-none" v-if="!form.contato_principal">
                      <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <button v-if="form.contato_principal" @click="form.contato_principal = null; searchContatoPrincipal = ''; telefoneContato = ''" type="button" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                      <svg class="h-4 w-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>

                    <div v-if="showContatosPrincipalDropdown && filteredContatosPrincipal.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-60 overflow-y-auto custom-scrollbar">
                      <div 
                        v-for="c in filteredContatosPrincipal" :key="c.id"
                        @click="selectContatoPrincipal(c)"
                        class="p-3 hover:bg-primary-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                      >
                        <div class="font-bold text-gray-900 text-sm">{{ c.nome }}</div>
                        <div class="text-[10px] text-gray-500">{{ c.celular || c.telefone || 'Sem telefone' }}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Telefone (Mandatory) -->
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1.5">Telefone <span class="text-red-500">*</span></label>
                    <input 
                      v-model="telefoneContato" 
                      type="tel" 
                      class="input" 
                      placeholder="(XX) 9XXXX-XXXX" 
                      required
                      @input="formatPhone"
                    />
                </div>

                <!-- Fonte (Select) -->
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1.5">Fonte <span class="text-red-500">*</span></label>
                    <select v-model="form.origem" class="input" required>
                      <option :value="null">Selecione a fonte...</option>
                      <option v-for="o in origens" :key="o.id" :value="o.id">{{ o.nome }}</option>
                    </select>
                </div>
            </div>

            <!-- Row 2: Nome -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">
                Nome da Oportunidade <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.nome"
                type="text"
                required
                class="input focus:ring-primary-500"
                placeholder="Ex: Venda de Sistema - Empresa XYZ"
              />
            </div>

            <!-- Row 3: Funil e Estagio (Hidden on Create) -->
            <div v-if="isEdit" class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1.5">Funil</label>
                <select v-model="form.funil" required class="input">
                  <option :value="null">Selecione o funil...</option>
                  <option v-for="f in funis" :key="f.id" :value="f.id">{{ f.nome }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-bold text-gray-700 mb-1.5">Estágio</label>
                <select v-model="form.estagio" required class="input" :disabled="!form.funil">
                  <option v-for="e in estagios" :key="e.id" :value="e.id">{{ e.nome }}</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <!-- 2. Comercial (Sidebar Matching Flow) -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-primary-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-primary-200 mr-3"></span>
            Dados Comerciais
          </h3>
          
          <div class="space-y-6">
            
            <!-- 1. Responsável -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Responsável</label>
              <select v-model="form.proprietario" class="input">
                 <option :value="null">Selecione...</option>
                 <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.first_name }} {{ u.last_name }}</option>
              </select>
            </div>

            <!-- 2. Valor -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Valor Estimado (R$)</label>
              <input v-model.number="form.valor_estimado" type="number" step="0.01" class="input" placeholder="0,00" />
            </div>

            <!-- 3. Produto (Plano) -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Produto (Plano)</label>
              <select v-model="form.plano" class="input">
                 <option :value="null">Selecione...</option>
                 <option v-for="p in planos" :key="p.id" :value="p.id">{{ p.nome }} (R$ {{ p.preco_mensal }})</option>
              </select>
            </div>

            <!-- 4. Adicionais (Dropdown) -->
            <div class="relative">
               <label class="block text-sm font-bold text-gray-700 mb-1.5">Adicionais (Upgrade)</label>
               <div class="relative">
                  <!-- Trigger -->
                  <button 
                     type="button"
                     @click="showAdicionaisDropdown = !showAdicionaisDropdown"
                     class="w-full py-2 px-3 bg-white border border-gray-300 rounded-lg text-left focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent flex justify-between items-center transition-shadow shadow-sm hover:border-gray-400"
                  >
                      <span class="text-sm text-gray-700 truncate pr-2">
                          {{ formatSelectedAdicionais() || 'Selecione...' }}
                      </span>
                      <svg class="w-4 h-4 text-gray-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                  </button>

                  <!-- Dropdown Content -->
                  <div v-if="showAdicionaisDropdown" class="absolute left-0 top-full mt-1 w-full bg-white border border-gray-200 shadow-xl rounded-lg z-50 p-2 max-h-60 overflow-y-auto">
                     <div class="space-y-1">
                        <div v-for="adc in adicionais_opcoes" :key="adc.id" class="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer transition-colors" @click.stop="toggleAdicional(adc.id, !hasAdicional(adc.id))">
                           <input 
                              type="checkbox" 
                              :value="adc.id" 
                              :checked="hasAdicional(adc.id)"
                              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 h-4 w-4 pointer-events-none"
                           />
                           <span class="text-sm text-gray-700 select-none">{{ adc.nome }}</span>
                        </div>
                     </div>
                  </div>
                  
                  <!-- Backdrop to close -->
                  <div v-if="showAdicionaisDropdown" class="fixed inset-0 z-40 bg-transparent cursor-default" @click="showAdicionaisDropdown = false"></div>
               </div>
            </div>

            <div class="border-t border-gray-200"></div>

            <!-- 5. Origem (Canal) -->
            <div>
                 <label class="block text-sm font-bold text-gray-700 mb-1.5">Canal de Aquisição</label>
                 <select v-model="form.canal" class="input">
                    <option :value="null">Selecione...</option>
                    <option v-for="c in canais" :key="c.id" :value="c.id">{{ c.nome }}</option>
                 </select>
            </div>

            <!-- 6. Previsão -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1.5">Previsão Fechamento</label>
                  <input v-model="form.data_fechamento_esperada" type="date" class="input" />
                </div>
                
                <div>
                  <label class="block text-sm font-bold text-gray-700 mb-1.5">Probabilidade (%)</label>
                  <input v-model.number="form.probabilidade" type="number" min="0" max="100" class="input" />
                </div>
            </div>

             <!-- 7. Indicador (Extra) -->
            <div>
                 <label class="block text-sm font-bold text-gray-700 mb-1.5">Indicador de Comissão</label>
                 <select v-model="form.indicador_comissao" class="input">
                     <option :value="null">Sem indicador...</option>
                     <option v-for="u in usuarios" :key="u.id" :value="u.id">{{ u.first_name }} {{ u.last_name }}</option>
                 </select>
            </div>

          </div>
        </section>

        <!-- 3. Entidades (Empresa/Contato) -->
        <section class="bg-gray-50/50 p-6 rounded-2xl border border-gray-100">
          <h3 class="text-xs font-black text-indigo-600 uppercase tracking-[0.2em] mb-6 flex items-center">
            <span class="w-8 h-px bg-indigo-200 mr-3"></span>
             Cliente e Contatos
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div class="relative">
              <label class="text-sm font-bold text-gray-700 mb-1.5 flex justify-between">
                <span>Empresa Principal <span class="text-red-500">*</span></span>
                <button type="button" @click="showNovaEmpresaModal = true" class="text-primary-600 hover:text-primary-700 text-[10px] font-black uppercase tracking-wider">+ Nova Empresa</button>
              </label>
              
              <div class="relative group">
                <input 
                  v-model="searchContaPrincipal" 
                  type="text" 
                  class="input pl-10 pr-10" 
                  placeholder="Buscar empresa..."
                  @focus="showContasPrincipalDropdown = true"
                >
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <button v-if="form.conta" @click="form.conta = null; searchContaPrincipal = ''" type="button" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg class="h-4 w-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                <div v-if="showContasPrincipalDropdown && filteredContasPrincipal.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-60 overflow-y-auto custom-scrollbar">
                  <div 
                    v-for="c in filteredContasPrincipal" :key="c.id"
                    @click="selectContaPrincipal(c)"
                    class="p-3 hover:bg-primary-50 cursor-pointer border-b border-gray-50 last:border-0 transition-colors"
                  >
                    <div class="font-bold text-gray-900 text-sm">{{ c.nome_empresa }}</div>
                    <div class="text-[10px] text-gray-500">{{ c.cnpj || 'Sem CNPJ' }}</div>
                  </div>
                </div>
              </div>
            </div>



            <!-- M2M Contatos -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-3">Contatos Extras</label>
              <div class="relative mb-4">
                <input 
                  v-model="searchM2MContato" 
                  type="text" 
                  class="input text-xs" 
                  placeholder="Buscar contato para vincular..."
                  @focus="showM2MContatosDropdown = true"
                >
                <div v-if="showM2MContatosDropdown && filteredM2MContatos.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-48 overflow-y-auto">
                  <div 
                    v-for="c in filteredM2MContatos" :key="c.id"
                    @click="addContatoM2M(c)"
                    class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs"
                  >
                    {{ c.nome }} <span class="text-gray-400">({{ c.conta_nome || 'S/ Empresa' }})</span>
                  </div>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="cId in form.contatos" :key="cId"
                  class="inline-flex items-center px-2.5 py-1.5 rounded-lg bg-white border border-gray-100 text-xs font-bold text-gray-700 shadow-sm"
                >
                  {{ getContatoNome(cId) }}
                  <button type="button" @click="removeContatoM2M(cId)" class="ml-2 text-gray-400 hover:text-red-500">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </span>
              </div>
            </div>

            <!-- M2M Empresas -->
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-3">Empresas Extras</label>
              <div class="relative mb-4">
                <input 
                  v-model="searchM2MEmpresa" 
                  type="text" 
                  class="input text-xs" 
                  placeholder="Buscar empresa para vincular..."
                  @focus="showM2MEmpresasDropdown = true"
                >
                <div v-if="showM2MEmpresasDropdown && filteredM2MEmpresas.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-2xl rounded-xl border border-gray-100 max-h-48 overflow-y-auto">
                  <div 
                    v-for="c in filteredM2MEmpresas" :key="c.id"
                    @click="addEmpresaM2M(c)"
                    class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs"
                  >
                    {{ c.nome_empresa }}
                  </div>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="eId in form.empresas" :key="eId"
                  class="inline-flex items-center px-2.5 py-1.5 rounded-lg bg-white border border-gray-100 text-xs font-bold text-gray-700 shadow-sm"
                >
                  {{ getEmpresaNome(eId) }}
                  <button type="button" @click="removeEmpresaM2M(eId)" class="ml-2 text-gray-400 hover:text-red-500">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Observações -->
        <section>
          <label class="block text-sm font-bold text-gray-700 mb-1.5">Detalhamento / Contexto</label>
          <textarea v-model="form.descricao" rows="4" class="input" placeholder="Anote aqui informações importantes da negociação..."></textarea>
        </section>
      </form>

      <!-- Coluna Lateral (Informações Rápidas, Anexos e Diagnósticos) -->
      <aside class="space-y-6">
        <!-- Status Card -->
        <div v-if="isEdit" class="bg-primary-600 rounded-2xl p-6 text-white shadow-xl shadow-primary-100">
          <div class="text-[10px] font-black uppercase tracking-[0.2em] opacity-80 mb-2">Responsável</div>
          <div class="flex items-center gap-3">
             <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center font-bold">{{ props.oportunidade?.proprietario_nome?.charAt(0) }}</div>
             <div>
               <div class="font-bold">{{ props.oportunidade?.proprietario_nome }}</div>
               <div class="text-[10px] opacity-70">{{ props.oportunidade?.canal_nome }}</div>
             </div>
          </div>
        </div>

        <!-- Seção de Anexos -->
        <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h4 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-4 flex justify-between items-center">
            Anexos
            <label class="cursor-pointer text-primary-600 hover:text-primary-700 font-black tracking-normal">
              <input type="file" class="hidden" @change="handleFileUpload" multiple>
              + Adicionar
            </label>
          </h4>
          
          <div v-if="anexos.length > 0" class="space-y-3">
            <div v-for="anexo in anexos" :key="anexo.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-xl group hover:bg-white border border-transparent hover:border-gray-100 transition-all">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm">
                  <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                </div>
                <div class="min-w-0">
                  <div class="text-xs font-bold text-gray-700 truncate" :title="anexo.nome">{{ anexo.nome }}</div>
                  <div class="text-[9px] text-gray-400">{{ formatDateShort(anexo.data_upload) }}</div>
                </div>
              </div>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <a :href="anexo.arquivo" target="_blank" class="p-1.5 text-gray-400 hover:text-primary-600"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg></a>
                <button type="button" @click="deleteAnexo(anexo.id)" class="p-1.5 text-gray-400 hover:text-red-500"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
             <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-loose">Sem arquivos</p>
          </div>
        </div>

        <!-- Diagnósticos de Maturidade -->
        <div v-if="diagnosticos.length > 0" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h4 class="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">Maturidade (Diagnóstico)</h4>
          <div class="space-y-4">
            <div v-for="diag in diagnosticos" :key="diag.id" class="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 relative group overflow-hidden">
               <div class="flex justify-between items-center mb-3">
                 <span class="text-[10px] font-black text-indigo-600 uppercase">{{ formatDateShort(diag.data_conclusao) }}</span>
                 <button @click="verDiagnostico(diag)" class="text-[10px] font-black text-indigo-500 hover:underline">Ver Detalhes</button>
               </div>
               <div class="grid grid-cols-2 gap-2">
                 <div v-for="(pilar, nome) in diag.pontuacao_por_pilar" :key="nome" class="text-center">
                    <div class="text-[8px] font-black text-gray-400 uppercase truncate" :title="nome">{{ nome }}</div>
                    <div class="text-sm font-black text-indigo-600">{{ pilar.score }}</div>
                 </div>
               </div>
            </div>
          </div>
        </div>

       <!-- Timeline Unificada (Substitui Histórico Antigo) -->
        <div v-if="isEdit" class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden h-[600px] flex flex-col">
           <TimelineFeed 
              model="oportunidade" 
              :id="form.id" 
              @action="(type) => console.log('Action triggered:', type)" 
           />
        </div>

        <!-- Histórico de Estágios (Legado - Manter escondido ou remover futuramente) -->
        <div v-if="isEdit && historico.length > 0 && false" class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
           <h4 class="text-xs font-black text-amber-400 uppercase tracking-widest mb-4">Track de Evolução</h4>
           <div class="space-y-4 relative">
             <div v-for="(item, idx) in historico.slice(0, 5)" :key="item.id" class="flex gap-3 relative">
                <div class="flex flex-col items-center">
                  <div class="w-2 h-2 rounded-full bg-amber-400"></div>
                  <div v-if="idx !== 0" class="w-px flex-1 bg-amber-100"></div>
                </div>
                <div class="pb-4 border-b border-gray-50 last:border-0 w-full">
                   <div class="text-[10px] font-black text-gray-800 tracking-tight">{{ item.nome_estagio_novo }}</div>
                   <div class="text-[8px] text-gray-400 mt-0.5">{{ formatDateShort(item.data_mudanca) }} • {{ item.usuario_nome }}</div>
                </div>
             </div>
           </div>
        </div>
      </aside>
    </div>

    <!-- Modais Auxiliares -->
    <ContaModal
      :show="showNovaEmpresaModal"
      @close="showNovaEmpresaModal = false"
      @saved="handleNovaEmpresaSaved"
    />
    <ContatoModal
      :show="showNovoContatoModal"
      :fixed-conta-id="form.conta"
      @close="showNovoContatoModal = false"
      @saved="handleNovoContatoSaved"
    />
  </BaseModal>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import BaseModal from './BaseModal.vue'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'
import { useAuthStore } from '@/stores/auth'
import ContaModal from './ContaModal.vue'
import ContatoModal from './ContatoModal.vue'
import TimelineFeed from './TimelineFeed.vue'

const authStore = useAuthStore()

const props = defineProps({
  show: Boolean,
  oportunidade: Object,
  fixedContaId: [Number, String],
  fixedFunilId: [Number, String],
  fixedEstagioId: [Number, String]
})

const emit = defineEmits(['close', 'saved'])

const form = ref({
  id: null,
  nome: '',
  conta: null,
  contato_principal: null,
  funil: null,
  estagio: null,
  valor_estimado: 0,
  data_fechamento_esperada: '',
  probabilidade: 0,
  descricao: '',
  canal: null,
  indicador_comissao: null,
  fonte: '',
  contatos: [],
  empresas: [],
  proprietario: null,
  plano: null,
  adicionais_itens: []
})

// ... (existing helper functions)

function hasAdicional(adicionalId) {
    if (!form.value.adicionais_itens) return false;
    return form.value.adicionais_itens.some(item => item.adicional === adicionalId);
}

function toggleAdicional(adicionalId, checked) {
    if (!form.value.adicionais_itens) form.value.adicionais_itens = [];
    
    if (checked) {
        form.value.adicionais_itens.push({
            adicional: adicionalId,
            quantidade: 1
        });
    } else {
        form.value.adicionais_itens = form.value.adicionais_itens.filter(item => item.adicional !== adicionalId);
    }
}

// ...

watch(() => props.oportunidade, async (newOp) => {
  if (newOp) {
    isEdit.value = true
    form.value = { 
       ...newOp,
       contatos: newOp.contatos || [],
       empresas: newOp.empresas || [],
       adicionais_itens: newOp.adicionais_detalhes?.map(d => ({
           adicional: d.adicional,
           quantidade: d.quantidade
       })) || []
    }
    // ...
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

async function loadOptions() {
  try {
    console.log('[loadOptions] Starting...')
    const [cRes, ctRes, fnRes, cnRes, uRes, pRes, adcRes, orRes] = await Promise.all([
      api.get('/contas/'),
      api.get('/contatos/'),
      api.get('/funis/'),
      api.get('/canais/'),
      api.get('/usuarios/'),
      api.get('/planos/'),
      api.get('/adicionais-plano/'),
      api.get('/origens/')
    ])
    console.log('[loadOptions] pRes:', pRes.data)
    console.log('[loadOptions] orRes:', orRes.data)
    
    contas.value = cRes.data.results || cRes.data
    contatos.value = ctRes.data.results || ctRes.data
    funis.value = (fnRes.data.results || fnRes.data).filter(f => f.tipo === 'OPORTUNIDADE')
    canais.value = cnRes.data.results || cnRes.data
    usuarios.value = uRes.data.results || uRes.data
    planos.value = pRes.data.results || pRes.data
    adicionais_opcoes.value = adcRes.data.results || adcRes.data
    origens.value = orRes.data.results || orRes.data
    
    console.log('[loadOptions] planos.value:', planos.value)
    console.log('[loadOptions] origens.value:', origens.value)
  } catch (err) { console.error('[loadOptions] ERROR:', err) }
}

// ...

function resetForm() {
  form.value = {
    nome: '',
    conta: props.fixedContaId ? parseInt(props.fixedContaId) : null,
    contato_principal: null,
    funil: props.fixedFunilId ? parseInt(props.fixedFunilId) : null,
    estagio: props.fixedEstagioId ? parseInt(props.fixedEstagioId) : null,
    valor_estimado: 0,
    probabilidade: 0,
    contatos: [],
    empresas: [],
    proprietario: authStore.user?.id || null, // Default to current user
    plano: null,
    adicionais_itens: [],
    origem: null
  }
  searchContaPrincipal.value = ''
  searchContatoPrincipal.value = ''
  telefoneContato.value = ''
  anexos.value = []
}

const loading = ref(false)
const isEdit = ref(false)
const contas = ref([])
const contatos = ref([])
const estagios = ref([])
const canais = ref([])
const funis = ref([])
const historico = ref([])
const anexos = ref([])
const diagnosticos = ref([])

// Comercial Options
const usuarios = ref([])
const planos = ref([])
const adicionais_opcoes = ref([])
const origens = ref([])
const showAdicionaisDropdown = ref(false)

function formatSelectedAdicionais() {
    if (!form.value.adicionais_itens || form.value.adicionais_itens.length === 0) return ''
    const names = form.value.adicionais_itens.map(item => {
        const opt = adicionais_opcoes.value.find(o => o.id === item.adicional)
        return opt ? opt.nome : '?'
    })
    return names.join(', ')
}

const showNovaEmpresaModal = ref(false)
const showNovoContatoModal = ref(false)

// Autocomplete Logic
const searchContaPrincipal = ref('')
const showContasPrincipalDropdown = ref(false)
const filteredContasPrincipal = computed(() => {
  if (!searchContaPrincipal.value) return contas.value.slice(0, 10)
  return contas.value.filter(c => 
    c.nome_empresa.toLowerCase().includes(searchContaPrincipal.value.toLowerCase())
  ).slice(0, 10)
})

const searchContatoPrincipal = ref('')
const telefoneContato = ref('') // Phone field for new/selected contact
const showContatosPrincipalDropdown = ref(false)
const filteredContatosPrincipal = computed(() => {
  const base = form.value.conta ? contatos.value.filter(c => c.conta === form.value.conta) : contatos.value
  if (!searchContatoPrincipal.value) return base.slice(0, 10)
  return base.filter(c => 
    c.nome.toLowerCase().includes(searchContatoPrincipal.value.toLowerCase())
  ).slice(0, 10)
})

// M2M Search Logic
const searchM2MContato = ref('')
const showM2MContatosDropdown = ref(false)
const filteredM2MContatos = computed(() => {
  if (!searchM2MContato.value) return contatos.value.slice(0, 10)
  return contatos.value.filter(c => 
    c.nome.toLowerCase().includes(searchM2MContato.value.toLowerCase()) &&
    !form.value.contatos.includes(c.id)
  ).slice(0, 10)
})

const searchM2MEmpresa = ref('')
const showM2MEmpresasDropdown = ref(false)
const filteredM2MEmpresas = computed(() => {
  if (!searchM2MEmpresa.value) return contas.value.slice(0, 10)
  return contas.value.filter(c => 
    c.nome_empresa.toLowerCase().includes(searchM2MEmpresa.value.toLowerCase()) &&
    !form.value.empresas.includes(c.id)
  ).slice(0, 10)
})

function selectContaPrincipal(c) {
  form.value.conta = c.id
  searchContaPrincipal.value = c.nome_empresa
  showContasPrincipalDropdown.value = false
}

function selectContatoPrincipal(c) {
  form.value.contato_principal = c.id
  searchContatoPrincipal.value = c.nome
  telefoneContato.value = c.celular || c.telefone || ''
  showContatosPrincipalDropdown.value = false
}

function addContatoM2M(c) {
  if (!form.value.contatos.includes(c.id)) {
    form.value.contatos.push(c.id)
  }
  searchM2MContato.value = ''
  showM2MContatosDropdown.value = false
}

function removeContatoM2M(id) {
  form.value.contatos = form.value.contatos.filter(c => c !== id)
}

function addEmpresaM2M(c) {
  if (!form.value.empresas.includes(c.id)) {
    form.value.empresas.push(c.id)
  }
  searchM2MEmpresa.value = ''
  showM2MEmpresasDropdown.value = false
}

function removeEmpresaM2M(id) {
  form.value.empresas = form.value.empresas.filter(e => e !== id)
}

function formatPhone() {
  // Brazilian phone mask: (XX) 9XXXX-XXXX
  let digits = telefoneContato.value.replace(/\D/g, '')
  if (digits.length > 11) digits = digits.slice(0, 11)
  
  if (digits.length === 0) {
    telefoneContato.value = ''
  } else if (digits.length <= 2) {
    telefoneContato.value = `(${digits}`
  } else if (digits.length <= 7) {
    telefoneContato.value = `(${digits.slice(0,2)}) ${digits.slice(2)}`
  } else {
    telefoneContato.value = `(${digits.slice(0,2)}) ${digits.slice(2,7)}-${digits.slice(7)}`
  }
}

function getContatoNome(id) {
  return contatos.value.find(c => c.id === id)?.nome || '...'
}

function getEmpresaNome(id) {
  return contas.value.find(c => c.id === id)?.nome_empresa || '...'
}

// Helper to load stages
async function updateEstagios(funilId) {
  if (!funilId) {
      estagios.value = []
      return
  }
  try {
      const response = await api.get(`/funis/${funilId}/estagios/`)
      const raw = response.data.results || response.data
      estagios.value = raw.map(v => ({
        id: v.estagio_id,
        nome: v.nome,
        tipo: v.tipo,
        is_padrao: v.is_padrao
      }))

      if (!isEdit.value && !form.value.estagio) {
        const defaultEstagio = estagios.value.find(e => e.is_padrao) || estagios.value[0]
        if (defaultEstagio) form.value.estagio = defaultEstagio.id
      }
  } catch (error) {
      console.error('Erro ao carregar estágios:', error)
      estagios.value = []
  }
}

// Watchers
watch(() => props.show, async (newVal) => {
  if (newVal) {
    await loadOptions()
    if (!isEdit.value) {
      if (props.fixedContaId) {
        form.value.conta = parseInt(props.fixedContaId)
        const c = contas.value.find(x => x.id === form.value.conta)
        if (c) searchContaPrincipal.value = c.nome_empresa
      }
      
      if (props.fixedFunilId) {
          const fid = parseInt(props.fixedFunilId)
          // If value is different, watcher will handle it.
          // If value is same, watcher won't trigger, so we must call manual update to be sure stages are loaded/reset.
          if (form.value.funil !== fid) {
             form.value.funil = fid
             // Watcher triggers
          } else {
             // Same value, manual trigger
             await updateEstagios(fid)
          }
      }
      
      if (props.fixedEstagioId) form.value.estagio = parseInt(props.fixedEstagioId)
      
      // Auto-select cheapest plan
      if (planos.value.length > 0) {
        const cheapest = planos.value.reduce((min, p) => 
          (!min || Number(p.preco_mensal) < Number(min.preco_mensal)) ? p : min
        , null)
        if (cheapest) form.value.plano = cheapest.id
      }
      
      // Garantir que proprietário é o usuário logado
      if (!form.value.proprietario) {
        form.value.proprietario = authStore.user?.id || null
      }
    }
  }
})

watch(() => form.value.funil, async (newFunil) => {
    await updateEstagios(newFunil)
})


watch(searchContatoPrincipal, (val) => {
    if (!isEdit.value) {
        form.value.nome = val
    }
})

async function handleSubmit() {
  if (!searchContatoPrincipal.value.trim() && !form.value.contato_principal) {
      alert('Obrigatório informar o Contato Principal.')
      return
  }
  if (!form.value.origem) {
      alert('Obrigatório informar a Fonte.')
      return
  }
  if (!telefoneContato.value.trim()) {
      alert('Obrigatório informar o Telefone.')
      return
  }

  loading.value = true
  try {
    // 1. Auto-create Company if typed but not selected
    if (!form.value.conta && searchContaPrincipal.value.trim()) {
      try {
        const res = await api.post('/contas/', { 
          nome_empresa: searchContaPrincipal.value,
          email: '', // Optional defaults
          telefone: ''
        })
        form.value.conta = res.data.id
        contas.value.unshift(res.data) // Add to local list
      } catch (e) {
        console.error("Erro ao criar empresa automática:", e)
        // Decide if we abort or continue. Let's alert and abort to be safe.
        alert('Erro ao criar empresa automática: ' +  (e.response?.data?.detail || e.message))
        loading.value = false
        return
      }
    }

    // 2. Auto-create Contact if typed but not selected
    if (!form.value.contato_principal && searchContatoPrincipal.value.trim()) {
      try {
        const payload = {
          nome: searchContatoPrincipal.value,
          email: null,
          telefone: null,
          celular: telefoneContato.value.trim() || null,
          cargo: ''
        }
        // Link to company if we have one (either selected or just created)
        if (form.value.conta) {
          payload.conta = form.value.conta
        }

        const res = await api.post('/contatos/', payload)
        form.value.contato_principal = res.data.id
        contatos.value.unshift(res.data)
      } catch (e) {
        console.error("Erro ao criar contato automático:", e)
        alert('Erro ao criar contato automático: ' + (e.response?.data?.detail || e.message))
        loading.value = false
        return
      }
    }

    const payload = { ...form.value }
    if (payload.id === null) delete payload.id

    // Sanitize fields to avoid 400 Bad Request
    if (!payload.data_fechamento_esperada) payload.data_fechamento_esperada = null
    if (payload.valor_estimado === '') payload.valor_estimado = null
    if (!payload.conta) payload.conta = null
    if (!payload.proprietario) payload.proprietario = null
    if (!payload.canal) payload.canal = null
    if (!payload.plano) payload.plano = null
    if (!payload.indicador_comissao) payload.indicador_comissao = null
    if (!payload.probabilidade && payload.probabilidade !== 0) payload.probabilidade = 0
    
    if (isEdit.value) {
      await api.put(`/oportunidades/${payload.id}/`, payload)
    } else {
      await api.post('/oportunidades/', payload)
    }
    emit('saved')
    emit('close')
    resetForm()
  } catch (err) {
    console.error(err)
    alert('Erro ao salvar oportunidade: ' + (err.response?.data?.detail || err.message))
  } finally { loading.value = false }
}

function formatDateShort(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

function handleNovaEmpresaSaved(conta) {
  contas.value.unshift(conta)
  selectContaPrincipal(conta)
  showNovaEmpresaModal.value = false
}

function handleNovoContatoSaved(contato) {
  contatos.value.unshift(contato)
  selectContatoPrincipal(contato)
  showNovoContatoModal.value = false
}

onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.group')) {
      showContasPrincipalDropdown.value = false
      showContatosPrincipalDropdown.value = false
      showM2MContatosDropdown.value = false
      showM2MEmpresasDropdown.value = false
    }
  })
})
</script>

<style scoped>
.input {
  @apply w-full px-4 py-3 rounded-xl border border-gray-200 bg-white shadow-sm transition-all focus:border-primary-500 focus:ring-4 focus:ring-primary-50 outline-none text-sm font-medium;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-200 rounded-full;
}
</style>
