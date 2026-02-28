<template>
  <div v-if="loading" class="flex items-center justify-center min-h-screen">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
  </div>

  <div v-else-if="oportunidade" class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Header de Negócio -->
    <header class="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-20">
      <div class="flex justify-between items-start">
        <div>
          <div class="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">
            <span class="cursor-pointer hover:text-primary-600" @click="goBack">Pipelines</span>
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            <span>{{ oportunidade.funil_nome || 'Funil Padrão' }}</span>
            <span v-if="oportunidade.id" class="text-gray-300">#{{ oportunidade.id }}</span>
          </div>
          <h1 class="text-2xl font-black text-gray-900 leading-tight">
            {{ oportunidade.nome }}
          </h1>
        </div>
        
        <div class="flex items-center gap-3">
          <div v-if="oportunidade.conta" class="hidden md:flex items-center gap-2">
            <select
              v-model="conversaoStatus"
              class="px-2 py-1 rounded-lg border border-gray-200 text-xs font-bold text-gray-700 bg-white"
            >
              <option value="CLIENTE_ATIVO">Cliente Ativo</option>
              <option value="INATIVO">Cliente Inativo</option>
            </select>
            <button
              @click="converterEmCliente"
              :disabled="convertendoCliente"
              class="px-3 py-2 rounded-lg text-xs font-black uppercase tracking-wider bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
              title="Converte a empresa da oportunidade em cliente"
            >
              {{ convertendoCliente ? 'Convertendo...' : 'Converter em cliente' }}
            </button>
          </div>

          <!-- Botão Cancelar -->
          <button 
            @click="goBack" 
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1"
            title="Cancelar e voltar ao Kanban"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span class="text-sm font-medium hidden sm:inline">Cancelar</span>
          </button>
          
          <div class="h-6 w-px bg-gray-200"></div>
          
          <button 
            @click="handleDelete" 
            class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Excluir Negócio"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </button>
          
          <div class="h-6 w-px bg-gray-200"></div>
          
          <button @click="saveChanges" class="btn btn-primary shadow-lg shadow-primary-200">
            Salvar
          </button>
        </div>
      </div>
      
      <!-- Barra de Estágios (Pipeline Visual) -->
      <div class="mt-6 flex items-stretch gap-1 overflow-x-auto pb-2 no-scrollbar">
        <div 
          v-for="(estagio, index) in estagios" 
          :key="estagio.id"
          @click="updateEstagio(estagio.id)"
          @mouseenter="hoveredEstagioId = estagio.id"
          @mouseleave="hoveredEstagioId = null"
          :title="estagio.id === oportunidade?.estagio 
            ? `${estagio.nome} (Estágio atual)` 
            : `Clique para mover para: ${estagio.nome}`"
          class="flex-1 min-w-[80px] py-2 px-3 rounded-lg cursor-pointer transition-all duration-200 relative group text-center"
          :class="[
            estagio.id === oportunidade?.estagio 
              ? 'ring-2 ring-offset-1 ring-primary-500 shadow-md scale-105 z-10' 
              : 'hover:scale-102 hover:shadow-md'
          ]"
          :style="{ 
            backgroundColor: (estagio.id === oportunidade?.estagio || hoveredEstagioId === estagio.id) 
              ? estagio.cor 
              : '#e5e7eb',
            color: (estagio.id === oportunidade?.estagio || hoveredEstagioId === estagio.id) 
              ? 'white' 
              : '#6b7280',
            opacity: (estagio.id === oportunidade?.estagio || hoveredEstagioId === estagio.id) ? 1 : 0.7
          }"
        >
          <span class="text-[10px] font-bold uppercase tracking-wide truncate block">
            {{ estagio.nome }}
          </span>
          <!-- Indicador de atual -->
          <div 
            v-if="estagio.id === oportunidade?.estagio" 
            class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-white border-2"
            :style="{ borderColor: estagio.cor }"
          ></div>
        </div>
      </div>
    </header>

    <div class="flex-1 w-full px-4 lg:px-6 grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6">
      
      <div class="lg:col-span-5 xl:col-span-5 flex flex-col gap-0 bg-white border-r border-gray-200 h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar rounded-xl shadow-sm">
        
        <!-- Sidebar Tabs -->
        <div class="flex items-center gap-4 px-6 border-b border-gray-100 text-[11px] font-bold text-gray-400 uppercase tracking-widest bg-white sticky top-0 z-10 transition-colors">
           <button 
             @click="activeSidebarTab = 'principal'"
             class="py-3 border-b-2 transition-colors duration-200"
             :class="activeSidebarTab === 'principal' ? 'text-primary-600 border-primary-600' : 'border-transparent hover:text-gray-600'"
           >
             Principal
           </button>
           <button 
             @click="activeSidebarTab = 'complementos'"
             class="py-3 border-b-2 transition-colors duration-200"
             :class="activeSidebarTab === 'complementos' ? 'text-primary-600 border-primary-600' : 'border-transparent hover:text-gray-600'"
           >
             Complementos
           </button>
           <button 
             @click="activeSidebarTab = 'estatisticas'"
             class="py-3 border-b-2 transition-colors duration-200"
             :class="activeSidebarTab === 'estatisticas' ? 'text-primary-600 border-primary-600' : 'border-transparent hover:text-gray-600'"
           >
             Estatísticas
           </button>

        </div>

        <!-- CONTEÚDO: PRINCIPAL -->
        <div v-if="activeSidebarTab === 'principal'">
            <!-- Campos do Negócio -->
            <div class="p-6 space-y-5 border-b border-gray-100">
               
               <!-- Responsável -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Responsável</label>
                  <div class="w-2/3">
                     <select 
                        v-model="oportunidadeForm.proprietario"
                        class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none appearance-none cursor-pointer"
                     >
                        <option :value="null">Selecione</option>
                        <option v-for="user in usuarios" :key="user.id" :value="user.id">
                           {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                        </option>
                     </select>
                  </div>
               </div>

               <!-- Venda (Valor) -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Venda</label>
                  <div class="w-2/3 relative">
                     <span class="absolute left-0 top-1/2 -translate-y-1/2 text-gray-400 text-sm">R$</span>
                     <input 
                        v-model="oportunidadeForm.valor_estimado"
                        type="number"
                        class="w-full pl-6 py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 font-bold focus:outline-none transition-colors text-right"
                        placeholder="0,00"
                     />
                  </div>
               </div>

               <!-- Produto (Plano) -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Faturamento</label>
                  <div class="w-2/3">
                     <select 
                        v-model="oportunidadeForm.plano"
                        class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none appearance-none cursor-pointer"
                     >
                        <option :value="null">Selecione...</option>
                        <option v-for="plano in planos" :key="plano.id" :value="plano.id">
                           {{ plano.nome }} (R$ {{ plano.preco_mensal }})
                        </option>
                     </select>
                  </div>
               </div>

               <!-- Adicionais (Upgrade) -->
               <div class="group flex items-center justify-between relative">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Adicionais (Upgrade)</label>
                  <div class="w-2/3 relative">
                     <!-- Trigger -->
                     <button 
                        @click="showAdicionaisDropdown = !showAdicionaisDropdown"
                        class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 cursor-pointer flex justify-between items-center text-left focus:outline-none"
                     >
                         <span class="text-sm text-gray-900 truncate pr-2">
                             {{ formatSelectedAdicionais() || 'Selecione...' }}
                         </span>
                         <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                     </button>

                     <!-- Dropdown Content -->
                     <div v-if="showAdicionaisDropdown" class="absolute left-0 top-full mt-1 w-full bg-white border border-gray-200 shadow-xl rounded-md z-50 p-2 max-h-60 overflow-y-auto">
                        <div class="space-y-1">
                           <div v-for="adc in adicionais_opcoes" :key="adc.id" class="flex items-center gap-2 p-1 hover:bg-gray-50 rounded cursor-pointer" @click.stop="toggleAdicional(adc.id, !hasAdicional(adc.id))">
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
                     
                     <!-- Backdrop para fechar ao clicar fora (opcional mas bom para UX) -->
                     <div v-if="showAdicionaisDropdown" class="fixed inset-0 z-40 bg-transparent cursor-default" @click="showAdicionaisDropdown = false"></div>
                  </div>
               </div>
               
                <div class="group flex items-center justify-between">
                   <label class="text-xs text-gray-400 font-medium w-1/3">Fonte / Origem</label>
                   <div class="w-2/3">
                      <div class="flex items-center justify-end w-full text-sm text-gray-600 font-medium py-1">
                         {{ oportunidade.origem_nome || oportunidade.fonte || 'Direto' }} 
                         <span class="text-gray-400 text-xs ml-2" v-if="oportunidade.data_criacao">
                            {{ formatDateShort(oportunidade.data_criacao) }}
                         </span>
                      </div>
                   </div>
                </div>

               <!-- Fechamento e Probabilidade -->
               <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                   <div class="group flex items-center justify-between">
                      <label class="text-xs text-gray-400 font-medium w-1/3">Previsão</label>
                      <div class="w-2/3">
                         <input 
                            type="date"
                            v-model="oportunidadeForm.data_fechamento_esperada"
                            @blur="saveChanges"
                            class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm text-right focus:outline-none"
                         />
                      </div>
                   </div>
                   <div class="group flex items-center justify-between">
                      <label class="text-xs text-gray-400 font-medium w-1/3 text-right pr-2">Prob. (%)</label>
                      <div class="w-2/3">
                         <input 
                            type="number"
                            min="0" max="100"
                            v-model.number="oportunidadeForm.probabilidade"
                            @blur="saveChanges"
                            class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                         />
                      </div>
                   </div>
               </div>

                <!-- Canal de Aquisição -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Canal</label>
                  <div class="w-2/3">
                     <select 
                        v-model="oportunidadeForm.canal"
                        @change="saveChanges"
                        class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none appearance-none cursor-pointer"
                     >
                        <option :value="null">Selecione...</option>
                        <option v-for="c in canais" :key="c.id" :value="c.id">{{ c.nome }}</option>
                     </select>
                  </div>
               </div>

               <!-- Indicador -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Indicador</label>
                  <div class="w-2/3">
                     <select 
                        v-model="oportunidadeForm.indicador_comissao"
                        @change="saveChanges"
                        class="w-full py-1 bg-transparent border-b border-transparent group-hover:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none appearance-none cursor-pointer"
                     >
                        <option :value="null">Sem indicador...</option>
                        <option v-for="c in indicadores" :key="c.id" :value="c.id">{{ c.nome }}</option>
                     </select>
                  </div>
               </div>
               
               <!-- Observações -->
               <div class="group">
                  <label class="text-xs text-gray-400 font-medium block mb-1">Detalhamento / Contexto</label>
                  <textarea 
                      v-model="oportunidadeForm.descricao" 
                      @blur="saveChanges"
                      rows="3" 
                      class="w-full py-2 px-3 bg-gray-50 border border-gray-100 rounded-lg group-hover:border-gray-200 focus:border-primary-500 focus:bg-white text-gray-900 text-sm focus:outline-none transition-colors custom-scrollbar" 
                      placeholder="Anote aqui informações importantes da negociação..."
                  ></textarea>
               </div>
               
               <!-- Tarefas Agendadas -->
               <div class="group flex items-center justify-between">
                  <label class="text-xs text-gray-400 font-medium w-1/3">Próxima Tarefa</label>
                   <div class="w-2/3 flex justify-end">
                     <div v-if="oportunidade.proxima_atividade" class="text-right">
                        <div class="text-sm font-bold text-gray-900 leading-tight">{{ oportunidade.proxima_atividade.titulo }}</div>
                        <div class="text-xs text-red-500 font-medium mt-0.5" v-if="new Date(oportunidade.proxima_atividade.data) < new Date()">
                           Vencida: {{ formatDateShort(oportunidade.proxima_atividade.data) }}
                        </div>
                        <div class="text-xs text-green-600 font-medium mt-0.5" v-else>
                           {{ formatDateShort(oportunidade.proxima_atividade.data) }}
                        </div>
                     </div>
                     <button v-else @click="handleTimelineAction('task')" class="text-xs text-primary-600 hover:underline flex items-center gap-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        Agendar
                     </button>
                   </div>
               </div>

            </div>

            <!-- Seção Contato (Editável) -->
            <div class="p-6 border-b border-gray-100 relative group/contact">
               <div class="flex items-start gap-4 mb-4">
                  <!-- Avatar -->
                  <div class="w-10 h-10 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-sm shrink-0 shadow-sm relative overflow-hidden">
                     <img v-if="oportunidade.contato_foto" :src="oportunidade.contato_foto" class="w-full h-full object-cover" />
                     <span v-else>{{ oportunidade.contato_nome?.charAt(0) || '?' }}</span>
                     <div class="absolute -bottom-1 -right-1 bg-green-500 rounded-full p-0.5 border border-white">
                        <svg class="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                     </div>
                  </div>

                  <div class="flex-1 min-w-0">
                     <div class="flex justify-between items-start">
                        <!-- Nome com link para modal se quiser full detail -->
                        <h3
                           v-if="oportunidade.contato_principal"
                           class="font-bold text-gray-900 truncate cursor-pointer hover:text-primary-600 hover:underline"
                           @click="goToContactDetail"
                        >
                           {{ oportunidade.contato_nome }}
                        </h3>
                        <h3 v-else class="font-bold text-gray-400 truncate">
                           Sem Contato
                        </h3>
                        <button class="text-gray-400 hover:text-gray-600">•••</button>
                     </div>
                     
                     <div class="mt-3 space-y-1">
                        <!-- Cargo (Posição) -->
                        <div class="flex items-center text-sm group/field">
                           <span class="text-gray-400 w-24 shrink-0">Posição</span>
                           <input 
                              v-if="oportunidade.contato_principal"
                              v-model="contactForm.cargo" 
                              @blur="saveContactField('cargo')"
                              class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                              placeholder="..."
                           />
                           <span v-else class="text-gray-300">...</span>
                        </div>

                         <!-- Telefone (Celular) -->
                         <div class="flex items-center text-sm group/field">
                            <span class="text-gray-400 w-24 shrink-0">Celular</span>
                            <div class="flex items-center gap-2 flex-1">
                               <input 
                                  v-if="oportunidade.contato_principal"
                                  v-model="contactForm.celular" 
                                  @input="formatPhoneLocal('celular')"
                                  @blur="saveContactField('celular')"
                                  class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                                  placeholder="(99) 99999-9999"
                               />
                               <span v-else class="text-gray-300 flex-1">...</span>
                               
                               <button v-if="oportunidade.contato_telefone || contactForm.celular" @click="openWhatsapp" class="text-green-500 hover:text-green-600" title="Chamar no WhatsApp">
                                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.539 2.016 2.041-.534c.945.512 1.99.782 3.245.782 3.181 0 5.766-2.587 5.768-5.766 0-3.181-2.587-5.766-5.866-5.751zm3.387 7.464c-.135-.067-.807-.399-.933-.444-.124-.045-.215-.067-.306.067-.09.135-.352.444-.43.534-.08.09-.158.101-.293.034-.135-.067-.57-.209-1.085-.67-.399-.356-.67-.795-.749-.933-.08-.135-.011-.202.056-.27.06-.06.135-.158.203-.237.067-.08.09-.135.135-.225.045-.09.022-.169-.011-.237-.034-.067-.306-.745-.421-.998-.103-.236-.211-.201-.306-.201h-.26c-.09 0-.237.034-.361.169s-.474.464-.474 1.13c0 .665.485 1.307.553 1.398.067.09.954 1.458 2.312 2.044.323.139.575.221.77.283.325.103.621.088.854.054.26-.039.807-.33 1.019-.648.214-.318.214-.593.15-.648-.063-.056-.233-.09-.368-.157z"/></svg>
                               </button>
                            </div>
                         </div>

                         <!-- Telefone Fixo -->
                         <div class="flex items-center text-sm group/field">
                            <span class="text-gray-400 w-24 shrink-0">Tel. comercial</span>
                            <input 
                               v-if="oportunidade.contato_principal"
                               v-model="contactForm.telefone" 
                               @input="formatPhoneLocal('telefone')"
                               @blur="saveContactField('telefone')"
                               class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                               placeholder="(99) 9999-9999"
                            />
                            <span v-else class="text-gray-300">...</span>
                         </div>

                        <!-- Email -->
                        <div class="flex items-center text-sm group/field">
                           <span class="text-gray-400 w-24 shrink-0">E-mail comercial</span>
                           <input 
                              v-if="oportunidade.contato_principal"
                              v-model="contactForm.email" 
                              @blur="saveContactField('email')"
                              class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-blue-600 font-medium underline focus:outline-none"
                              placeholder="..."
                           />
                           <span v-else class="text-gray-300">...</span>
                        </div>
                     </div>
                  </div>
               </div>
               
               <!-- Link: Adicionar contato -->
               <button v-if="!oportunidade.contato_principal" @click="openContactModal" class="flex items-center gap-2 text-gray-400 hover:text-primary-600 transition-colors mt-2 text-sm font-medium">
                  <div class="w-6 h-6 rounded-full border border-gray-300 flex items-center justify-center text-lg leading-none pb-0.5">+</div>
                  Adicionar contato
               </button>
            </div>

            <!-- Seção Empresa (Editável) -->
            <div class="p-6 relative group/company" v-if="oportunidade.conta || true"> <!-- Always show struct but hide if empty? user wants explicit form -->
               <div class="flex items-start gap-4 mb-4" v-if="oportunidade.conta">
                  <div class="w-10 h-10 rounded bg-gray-100 flex items-center justify-center text-gray-400 font-bold text-xs">
                     <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                  </div>
                   
                  <div class="flex-1 min-w-0">
                     <div class="flex justify-between items-start">
                        <!-- Nome Empresa -->
                        <div class="w-full">
                           <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block mb-0.5">Empresa</span>
                           <div class="flex items-center gap-2">
                             <h3 class="font-bold text-gray-900 leading-tight cursor-pointer hover:text-primary-600 hover:underline" @click="openCompanyModal">
                                {{ oportunidade.conta_nome }}
                             </h3>
                             <span
                               v-if="oportunidade.conta_dados?.status_cliente_display"
                               class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase"
                               :class="oportunidade.conta_dados?.status_cliente === 'CLIENTE_ATIVO' ? 'bg-emerald-100 text-emerald-700' : (oportunidade.conta_dados?.status_cliente === 'INATIVO' ? 'bg-gray-200 text-gray-700' : 'bg-blue-100 text-blue-700')"
                             >
                               {{ oportunidade.conta_dados.status_cliente_display }}
                             </span>
                           </div>
                        </div>
                        <button class="text-gray-400 hover:text-gray-600">•••</button>
                     </div>
                      
                     <div class="mt-3 space-y-1">
                        <!-- Site -->
                        <div class="flex items-center text-sm group/field">
                           <span class="text-gray-400 w-24 shrink-0">Site</span>
                           <input 
                              v-if="oportunidade.conta"
                              v-model="companyForm.website" 
                              @blur="saveCompanyField('website')"
                              class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                              placeholder="..."
                           />
                        </div>

                        <!-- Endereço (usando só um campo genérico para simplificar visualmente) -->
                        <div class="flex items-center text-sm group/field">
                           <span class="text-gray-400 w-24 shrink-0">Endereço</span>
                           <input 
                              v-if="oportunidade.conta"
                              v-model="companyForm.endereco" 
                              @blur="saveCompanyField('endereco')"
                              class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                              placeholder="..."
                           />
                        </div>

                        <!-- Email Comercial Empresa -->
                        <div class="flex items-center text-sm group/field">
                           <span class="text-gray-400 w-24 shrink-0">E-mail comercial</span>
                           <input 
                              v-if="oportunidade.conta"
                              v-model="companyForm.email" 
                              @blur="saveCompanyField('email')"
                              class="w-full bg-transparent border-b border-transparent group-hover/field:border-gray-200 focus:border-primary-500 text-gray-900 text-sm focus:outline-none"
                              placeholder="..."
                           />
                        </div>
                     </div>
                  </div>
               </div>

               <div v-else class="p-0">
                   <button @click="openCompanyModal" class="flex items-center gap-2 text-gray-400 hover:text-primary-600 transition-colors text-sm font-medium">
                      <div class="w-6 h-6 rounded-full border border-gray-300 flex items-center justify-center text-lg leading-none pb-0.5">+</div>
                      Adicionar empresa
                   </button>
               </div>
            </div>
        </div>

        <!-- CONTEÚDO: COMPLEMENTOS (Vínculos, Anexos, etc) -->
        <div v-else-if="activeSidebarTab === 'complementos'" class="p-6 space-y-6">
           
           <!-- Vínculos Adicionais -->
           <div class="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
             <h4 class="text-xs font-black text-indigo-500 uppercase tracking-widest mb-4">Vínculos Múltiplos</h4>
             
             <!-- M2M Contatos -->
             <div class="mb-4">
               <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Contatos Vinculados</label>
               <div class="relative mb-2">
                 <input
                   v-model="searchM2MContato"
                   type="text"
                   class="w-full py-1.5 px-3 bg-gray-50 border border-gray-100 rounded focus:border-primary-500 focus:bg-white text-gray-900 text-xs focus:outline-none transition-colors"
                   placeholder="Buscar contato para vincular..."
                   @focus="showM2MContatosDropdown = true"
                 >
                 <div v-if="showM2MContatosDropdown && filteredM2MContatos.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-xl rounded-lg border border-gray-100 max-h-48 overflow-y-auto custom-scrollbar">
                   <div
                     v-for="c in filteredM2MContatos" :key="c.id"
                     @click="addContatoM2M(c)"
                     class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs"
                   >
                     <span class="font-bold">{{ c.nome }}</span> <span class="text-gray-400">({{ c.conta_nome || 'S/ Empresa' }})</span>
                   </div>
                 </div>
                 
                 <!-- Backdrop M2M contatos -->
                 <div v-if="showM2MContatosDropdown" class="fixed inset-0 z-40 bg-transparent cursor-default" @click="showM2MContatosDropdown = false"></div>
               </div>
               <div class="flex flex-wrap gap-2">
                 <span
                   v-for="cId in oportunidadeForm.contatos" :key="'c'+cId"
                   class="inline-flex items-center px-2 py-1 rounded bg-indigo-50 border border-indigo-100 text-xs font-bold text-indigo-700"
                 >
                   {{ getContatoNome(cId) }}
                   <button type="button" @click="removeContatoM2M(cId)" class="ml-1 text-indigo-400 hover:text-red-500">
                     <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                   </button>
                 </span>
                 <p v-if="!oportunidadeForm.contatos?.length" class="text-xs text-gray-400 italic">Nenhum vínculo adicional.</p>
               </div>
             </div>

             <!-- M2M Empresas -->
             <div>
               <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Empresas Vinculadas</label>
               <div class="relative mb-2">
                 <input
                   v-model="searchM2MEmpresa"
                   type="text"
                   class="w-full py-1.5 px-3 bg-gray-50 border border-gray-100 rounded focus:border-primary-500 focus:bg-white text-gray-900 text-xs focus:outline-none transition-colors"
                   placeholder="Buscar empresa para vincular..."
                   @focus="showM2MEmpresasDropdown = true"
                 >
                 <div v-if="showM2MEmpresasDropdown && filteredM2MEmpresas.length > 0" class="absolute z-50 mt-1 w-full bg-white shadow-xl rounded-lg border border-gray-100 max-h-48 overflow-y-auto custom-scrollbar">
                   <div
                     v-for="c in filteredM2MEmpresas" :key="c.id"
                     @click="addEmpresaM2M(c)"
                     class="p-2 hover:bg-primary-50 cursor-pointer border-b border-gray-50 text-xs font-bold"
                   >
                     {{ c.nome_empresa }}
                   </div>
                 </div>
                 
                 <!-- Backdrop M2M empresas -->
                 <div v-if="showM2MEmpresasDropdown" class="fixed inset-0 z-40 bg-transparent cursor-default" @click="showM2MEmpresasDropdown = false"></div>
               </div>
               <div class="flex flex-wrap gap-2">
                 <span
                   v-for="eId in oportunidadeForm.empresas" :key="'e'+eId"
                   class="inline-flex items-center px-2 py-1 rounded bg-indigo-50 border border-indigo-100 text-xs font-bold text-indigo-700"
                 >
                   {{ getEmpresaNome(eId) }}
                   <button type="button" @click="removeEmpresaM2M(eId)" class="ml-1 text-indigo-400 hover:text-red-500">
                     <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                   </button>
                 </span>
                 <p v-if="!oportunidadeForm.empresas?.length" class="text-xs text-gray-400 italic">Nenhum vínculo adicional.</p>
               </div>
             </div>
           </div>

           <!-- Seção de Anexos -->
           <div class="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
             <h4 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-3 flex justify-between items-center">
               Anexos
               <label class="cursor-pointer text-primary-600 hover:text-primary-700 font-bold tracking-normal uppercase text-[10px] bg-primary-50 px-2 py-1 border border-primary-100 rounded">
                 <input type="file" class="hidden" @change="handleFileUpload" multiple>
                 + Adicionar
               </label>
             </h4>
             
             <div v-if="anexos.length > 0" class="space-y-2">
               <div v-for="anexo in anexos" :key="anexo.id" class="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg group hover:bg-white border border-transparent hover:border-gray-100 transition-all">
                 <div class="flex items-center gap-3 min-w-0">
                   <div class="w-8 h-8 rounded bg-white flex items-center justify-center shadow-sm shrink-0">
                     <svg class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                   </div>
                   <div class="min-w-0 flex-1">
                     <div class="text-xs font-bold text-gray-700 truncate" :title="anexo.nome">{{ anexo.nome }}</div>
                     <div class="text-[9px] text-gray-400">{{ formatDateShort(anexo.data_upload) }}</div>
                   </div>
                 </div>
                 <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                   <a :href="anexo.arquivo" target="_blank" class="p-1.5 text-gray-400 hover:text-primary-600"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg></a>
                   <button type="button" @click="deleteAnexo(anexo.id)" class="p-1.5 text-gray-400 hover:text-red-500"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg></button>
                 </div>
               </div>
             </div>
             <div v-else class="text-center py-6 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-loose">Sem arquivos</p>
             </div>
           </div>

           <!-- Diagnósticos de Maturidade -->
           <div v-if="diagnosticos && diagnosticos.length > 0" class="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
             <h4 class="text-xs font-black text-indigo-400 uppercase tracking-widest mb-3">Maturidade (Diagnóstico)</h4>
             <div class="space-y-3">
               <div v-for="diag in diagnosticos" :key="diag.id" class="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100 relative group overflow-hidden">
                  <div class="flex justify-between items-center mb-3 border-b border-indigo-100 pb-2">
                    <span class="text-[10px] font-black text-indigo-600 uppercase">{{ formatDateShort(diag.data_conclusao) }}</span>
                  </div>
                  <div class="grid grid-cols-2 gap-2 mt-2">
                    <div v-for="(pilar, nome) in diag.pontuacao_por_pilar" :key="nome" class="text-center bg-white p-1.5 rounded shadow-sm">
                       <div class="text-[8px] font-black text-gray-500 uppercase truncate" :title="nome">{{ nome }}</div>
                       <div class="text-sm font-black text-indigo-600">{{ pilar.score }}</div>
                    </div>
                  </div>
               </div>
             </div>
           </div>

        </div>
        
        <!-- CONTEÚDO: ESTATÍSTICAS (MANTIDO) -->
        <div v-else-if="activeSidebarTab === 'estatisticas'" class="p-6">
           <!-- Fonte -->
           <div class="mb-8">
              <span class="block text-gray-900 font-bold mb-1 text-sm">Fonte:</span>
              <div class="text-gray-500 text-sm">
                {{ oportunidade.fonte || 'Origem Desconhecida' }} / {{ formatDateShort(oportunidade.data_criacao) }}
              </div>
           </div>
           
           <!-- Dias Ativos -->
           <div class="mb-8">
               <div class="text-6xl font-light text-blue-500 mb-1 leading-none tracking-tight">
                   {{ daysActive }}
               </div>
               <div class="text-blue-500 text-sm">Dias ativos</div>
           </div>
           
           <!-- Lista de Métricas -->
           <div class="space-y-4">
               <div class="flex justify-between items-baseline text-sm">
                   <div class="text-gray-600">Chamadas <span class="text-gray-400 text-xs">recebidas / realizadas</span></div>
                   <div class="font-medium text-gray-900">0/0</div>
               </div>
               
               <div class="flex justify-between items-center text-sm">
                   <div class="text-gray-600">E-mails</div>
                   <div class="font-medium text-gray-900">0</div>
               </div>
               
               <div class="flex justify-between items-baseline text-sm">
                   <div class="text-gray-600">Tarefas <span class="text-gray-400 text-xs">finalizadas / <span class="text-red-300">vencidas</span></span></div>
                   <div class="font-medium"><span class="text-gray-900">0</span>/<span class="text-red-400">0</span></div>
               </div>
               
               <div class="flex justify-between items-center text-sm">
                   <div class="text-gray-600">Notas</div>
                   <div class="font-medium text-gray-900">0</div>
               </div>
               
               <div class="flex justify-between items-center text-sm">
                   <div class="text-gray-600">Bate-papo com o cliente</div>
                   <div class="font-medium text-gray-900">{{ oportunidade.whatsapp_nao_lidas || 0 }}</div>
               </div>
               
               <div class="flex justify-between items-center text-sm">
                   <div class="text-gray-600">Bate-papo interno</div>
                   <div class="font-medium text-gray-900">0</div>
               </div>
           </div>
           
           <div class="mt-8 pt-6 border-t border-gray-100">
               <div class="font-bold text-gray-900 text-sm mb-1">Informação rastreada:</div>
               <div class="text-sm text-gray-400">
                   Preenchida 0 de 10 <a href="#" class="underline hover:text-gray-600">Mostrar</a>
               </div>
           </div>
        </div>

      </div>

      <!-- Coluna Direita: Feed e Atividades -->
      <div class="lg:col-span-7 xl:col-span-7 bg-white rounded-xl shadow-sm border border-gray-200 h-[calc(100vh-140px)] flex flex-col overflow-hidden">
        <div class="flex-1 bg-gray-50/50">
           <TimelineFeed
             ref="timelineFeedRef"
             model="oportunidade"
             :id="oportunidade.id"
             class="h-full"
             @action="handleTimelineAction"
           />
        </div>
      </div>

    </div>

    <!-- Modais Auxiliares -->
    <ContatoModal 
      :show="showContactModal" 
      :contato="selectedContato"
      :fixed-conta-id="oportunidade.conta"
      @close="closeContactModal"
      @saved="refreshData"
    />
    
    <ContaModal
      :show="showCompanyModal"
      :conta="selectedCompany"
      @close="closeCompanyModal"
      @saved="refreshData"
    />
    
    <WhatsappChat
      :show="showWhatsappChat"
      :number="whatsappData.number"
      :title="whatsappData.title"
      :oportunidade="oportunidade.id"
      @close="showWhatsappChat = false"
    />

    <AtividadeModal
      :show="showAtividadeModal"
      :association-fixed="true"
      :initial-association="oportunidadeContentTypeId ? { content_type: oportunidadeContentTypeId, object_id: oportunidade.id } : null"
      :initial-tipo="initialTipoAtividade"
      @close="showAtividadeModal = false"
      @saved="handleAtividadeSaved"
    />
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useOportunidadesStore } from '@/stores/oportunidades'
import TimelineFeed from '@/components/TimelineFeed.vue'
import ContatoModal from '@/components/ContatoModal.vue'
import ContaModal from '@/components/ContaModal.vue'
import WhatsappChat from '@/components/WhatsappChat.vue'
import AtividadeModal from '@/components/AtividadeModal.vue'

const route = useRoute()
const router = useRouter()
const oportunidadesStore = useOportunidadesStore()

const loading = ref(true)
const oportunidade = ref(null)
const estagios = ref([])
const hoveredEstagioId = ref(null)

// Listas de Opções
const usuarios = ref([])
const planos = ref([])
const adicionais_opcoes = ref([])
const canais = ref([])
const contatos = ref([])
const indicadores = computed(() => contatos.value.filter(c => c.tipo === 'INDICADOR' || c.tipo_contato_nome?.toUpperCase() === 'INDICADOR'))

// Forms e Estados
const oportunidadeForm = ref({
  valor_estimado: 0,
  data_fechamento_esperada: '',
  probabilidade: 0,
  proprietario: null,
  plano: null,
  adicionais_itens: [],
  canal: null,
  indicador_comissao: null,
  descricao: '',
  contatos: [],
  empresas: []
})

// Forms Entidades Vinculadas (para edição direta)
const contactForm = ref({
    cargo: '',
    telefone: '',
    celular: '',
    email: ''
})

const companyForm = ref({
    website: '',
    endereco: '',
    email: ''
})

const activeSidebarTab = ref('principal')

// Modais
const showContactModal = ref(false)
const selectedContato = ref(null)

const showCompanyModal = ref(false)
const selectedCompany = ref(null)

const showWhatsappChat = ref(false)
const whatsappData = ref({})

const showAtividadeModal = ref(false)
const initialTipoAtividade = ref('TAREFA')
const oportunidadeContentTypeId = ref(null)
const timelineFeedRef = ref(null)
const conversaoStatus = ref('CLIENTE_ATIVO')
const convertendoCliente = ref(false)

// Computed
const daysActive = computed(() => {
  if (!oportunidade.value?.data_criacao) return 0
  
  const created = new Date(oportunidade.value.data_criacao)
  const now = new Date()
  const diffTime = Math.abs(now - created)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) 
  return diffDays
})

function formatDateShort(dateString) {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function hasAdicional(adicionalId) {
    if (!oportunidadeForm.value.adicionais_itens) return false;
    return oportunidadeForm.value.adicionais_itens.some(item => item.adicional === adicionalId);
}

function toggleAdicional(adicionalId, checked) {
    if (!oportunidadeForm.value.adicionais_itens) oportunidadeForm.value.adicionais_itens = [];
    
    if (checked) {
        oportunidadeForm.value.adicionais_itens.push({
            adicional: adicionalId,
            quantidade: 1
        });
    } else {
        oportunidadeForm.value.adicionais_itens = oportunidadeForm.value.adicionais_itens.filter(item => item.adicional !== adicionalId);
    }
    // Não faz auto-save - usuário precisa clicar em Salvar
}

const showAdicionaisDropdown = ref(false)

const anexos = ref([])
const diagnosticos = ref([])

// Novas Lists para M2M
const contas = ref([])

// M2M Search Logic
const searchM2MContato = ref('')
const showM2MContatosDropdown = ref(false)
const filteredM2MContatos = computed(() => {
  if (!searchM2MContato.value) return contatos.value.slice(0, 10)
  return contatos.value.filter(c => 
    c.nome.toLowerCase().includes(searchM2MContato.value.toLowerCase()) &&
    !(oportunidadeForm.value.contatos || []).includes(c.id)
  ).slice(0, 10)
})

const searchM2MEmpresa = ref('')
const showM2MEmpresasDropdown = ref(false)
const filteredM2MEmpresas = computed(() => {
  if (!searchM2MEmpresa.value) return contas.value.slice(0, 10)
  return contas.value.filter(c => 
    c.nome_empresa.toLowerCase().includes(searchM2MEmpresa.value.toLowerCase()) &&
    !(oportunidadeForm.value.empresas || []).includes(c.id)
  ).slice(0, 10)
})

function addContatoM2M(c) {
  if (!oportunidadeForm.value.contatos) oportunidadeForm.value.contatos = []
  if (!oportunidadeForm.value.contatos.includes(c.id)) {
    oportunidadeForm.value.contatos.push(c.id)
    saveChanges()
  }
  searchM2MContato.value = ''
  showM2MContatosDropdown.value = false
}

function removeContatoM2M(id) {
  oportunidadeForm.value.contatos = oportunidadeForm.value.contatos.filter(c => c !== id)
  saveChanges()
}

function addEmpresaM2M(c) {
  if (!oportunidadeForm.value.empresas) oportunidadeForm.value.empresas = []
  if (!oportunidadeForm.value.empresas.includes(c.id)) {
    oportunidadeForm.value.empresas.push(c.id)
    saveChanges()
  }
  searchM2MEmpresa.value = ''
  showM2MEmpresasDropdown.value = false
}

function removeEmpresaM2M(id) {
  oportunidadeForm.value.empresas = oportunidadeForm.value.empresas.filter(e => e !== id)
  saveChanges()
}

function getContatoNome(id) {
  return contatos.value.find(c => c.id === id)?.nome || 'Desconhecido'
}

function getEmpresaNome(id) {
  return contas.value.find(e => e.id === id)?.nome_empresa || 'Desconhecida'
}

// Upload Anexos
async function handleFileUpload(event) {
  const files = event.target.files
  if (!files.length) return
  
  for (let i = 0; i < files.length; i++) {
    const formData = new FormData()
    formData.append('arquivo', files[i])
    formData.append('nome', files[i].name)
    formData.append('oportunidade', oportunidade.value.id)
    
    try {
      const res = await api.post('/oportunidades-anexos/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      anexos.value.unshift(res.data)
    } catch (err) {
      console.error("Erro no upload do anexo", err)
    }
  }
  event.target.value = ''
}

async function deleteAnexo(id) {
  if (!confirm('Excluir anexo?')) return
  try {
    await api.delete(`/oportunidades-anexos/${id}/`)
    anexos.value = anexos.value.filter(a => a.id !== id)
  } catch (err) {
    console.error("Erro excluindo anexo", err)
  }
}

async function converterEmCliente() {
  if (!oportunidade.value?.conta) {
    alert('A oportunidade precisa ter empresa vinculada para conversão.')
    return
  }

  const statusLabel = conversaoStatus.value === 'INATIVO' ? 'Cliente Inativo' : 'Cliente Ativo'
  const ok = confirm(
    `Este processo NÃO gera vendas.\n\nEle converte a empresa desta oportunidade para "${statusLabel}" e registra auditoria.\nUse somente para oportunidades que já são clientes.\n\nDeseja continuar?`
  )
  if (!ok) return

  convertendoCliente.value = true
  try {
    const res = await api.post(`/oportunidades/${oportunidade.value.id}/converter_em_cliente/`, {
      status_cliente: conversaoStatus.value
    })
    alert(res.data?.mensagem || 'Conversão concluída.')
    await loadData()
  } catch (error) {
    console.error('Erro ao converter em cliente:', error)
    alert(error.response?.data?.error || 'Erro ao converter em cliente.')
  } finally {
    convertendoCliente.value = false
  }
}

function formatSelectedAdicionais() {
    if (!oportunidadeForm.value.adicionais_itens?.length) return ''
    
    // Mapeia IDs para Nomes
    const names = oportunidadeForm.value.adicionais_itens.map(item => {
        const found = adicionais_opcoes.value.find(op => op.id === item.adicional)
        return found ? found.nome : ''
    }).filter(n => n)
    
    if (names.length === 0) return ''
    if (names.length <= 2) return names.join(', ')
    return `${names.length} selecionados`
}

// Carregamento Inicial
onMounted(async () => {
  await loadAuxData()
  await loadData()
})

async function loadAuxData() {
    try {
        const [usersRes, planosRes, adicRes, ctRes, canaisRes, contatosRes, contasRes] = await Promise.all([
            api.get('/usuarios/'),
            api.get('/planos/'),
            api.get('/adicionais-plano/'),
            api.get('/atividades/content_types/'),
            api.get('/canais/'),
            api.get('/contatos/'),
            api.get('/contas/')
        ])
        usuarios.value = usersRes.data.results || usersRes.data
        planos.value = planosRes.data.results || planosRes.data
        adicionais_opcoes.value = adicRes.data.results || adicRes.data
        canais.value = canaisRes.data.results || canaisRes.data
        contatos.value = contatosRes.data.results || contatosRes.data
        contas.value = contasRes.data.results || contasRes.data
        const ct = (ctRes.data || []).find(t => t.model === 'oportunidade')
        if (ct) oportunidadeContentTypeId.value = ct.id
    } catch (err) {
        console.error("Erro carregando listas auxiliares", err)
    }
}

async function loadData() {
  loading.value = true
  try {
    const id = route.params.id
    
    // 1. Oportunidade
    const res = await api.get(`/oportunidades/${id}/`)
    oportunidade.value = res.data
    
    // Preencher form local
    oportunidadeForm.value = {
      valor_estimado: res.data.valor_estimado,
      data_fechamento_esperada: res.data.data_fechamento_esperada,
      probabilidade: res.data.probabilidade,
      proprietario: res.data.proprietario,
      plano: res.data.plano,
      canal: res.data.canal,
      indicador_comissao: res.data.indicador_comissao,
      descricao: res.data.descricao,
      contatos: res.data.contatos || [],
      empresas: res.data.empresas || [],
      adicionais_itens: res.data.adicionais_detalhes?.map(d => ({
          adicional: d.adicional,
          quantidade: d.quantidade
      })) || []
    }
    
    anexos.value = res.data.anexos_detalhe || []
    diagnosticos.value = res.data.diagnosticos_detalhe || []
    
    // Preencher Forms vinculados (Contato/Empresa)
    if (res.data.contato_principal_dados) {
        const c = res.data.contato_principal_dados
        contactForm.value = {
            cargo: c.cargo,
            telefone: c.telefone_formatado || (c.telefone ? c.telefone.replace(/^55/, '') : ''), 
            celular: c.celular_formatado || (c.celular ? c.celular.replace(/^55/, '') : ''),
            email: c.email
        }
        // Force formatting on load
        formatPhoneLocal('celular')
        formatPhoneLocal('telefone')
    } else {
        contactForm.value = { cargo: '', telefone: '', celular: '', email: '' }
    }
    
    if (res.data.conta_dados) {
        const emp = res.data.conta_dados
        companyForm.value = {
            website: emp.website,
            endereco: emp.endereco,
            email: emp.email
        }
        if (emp.status_cliente === 'INATIVO') {
          conversaoStatus.value = 'INATIVO'
        } else {
          conversaoStatus.value = 'CLIENTE_ATIVO'
        }
    } else {
        companyForm.value = { website: '', endereco: '', email: '' }
        conversaoStatus.value = 'CLIENTE_ATIVO'
    }

    // 2. Estágios do Funil
    if (res.data.funil) {
      const funilRes = await api.get(`/funis/${res.data.funil}/`)
      // Ordenar e planificar estágios
      estagios.value = funilRes.data.estagios_detalhe
        .sort((a, b) => a.ordem - b.ordem)
        .map(fe => ({
          id: fe.estagio_id,
          nome: fe.nome,
          cor: fe.cor
        }))
    }
  } catch (error) {
    console.error('Erro ao carregar oportunidade:', error)
    if (error.response?.status === 404) {
      router.push('/kanban')
    }
  } finally {
    loading.value = false
  }
}

// Ações
function goBack() {
  if (confirm('Deseja sair? As alterações não salvas serão perdidas.')) {
    router.push('/kanban')
  }
}

async function saveChanges() {
  try {
     // Prepara payload com apenas os campos editáveis e no formato correto
     const payload = {
       valor_estimado: oportunidadeForm.value.valor_estimado,
       data_fechamento_esperada: oportunidadeForm.value.data_fechamento_esperada || null,
       probabilidade: oportunidadeForm.value.probabilidade,
       proprietario: typeof oportunidadeForm.value.proprietario === 'object' 
         ? oportunidadeForm.value.proprietario?.id 
         : oportunidadeForm.value.proprietario,
       plano: typeof oportunidadeForm.value.plano === 'object'
         ? oportunidadeForm.value.plano?.id
         : oportunidadeForm.value.plano,
       canal: oportunidadeForm.value.canal,
       indicador_comissao: oportunidadeForm.value.indicador_comissao,
       descricao: oportunidadeForm.value.descricao,
       contatos: oportunidadeForm.value.contatos,
       empresas: oportunidadeForm.value.empresas,
       adicionais: oportunidadeForm.value.adicionais_itens || []
     }
     
     await api.patch(`/oportunidades/${oportunidade.value.id}/`, payload)
     
     // Sucesso - volta para o Kanban
     router.push('/kanban')
  } catch (error) {
    console.error('Erro ao salvar:', error)
    alert('Erro ao salvar alterações: ' + (error.response?.data?.detail || error.message))
  }
}

async function saveContactField(field) {
    if (!oportunidade.value.contato_principal) return;
    
    try {
        const payload = {}
        payload[field] = contactForm.value[field]
        await api.patch(`/contatos/${oportunidade.value.contato_principal}/`, payload)
        // Feedback visual sutil?
    } catch(err) {
        console.error("Erro salvando contato", err)
    }
}

async function saveCompanyField(field) {
    if (!oportunidade.value.conta) return;
    
    try {
        const payload = {}
        payload[field] = companyForm.value[field]
        await api.patch(`/contas/${oportunidade.value.conta}/`, payload)
    } catch(err) {
        console.error("Erro salvando empresa", err)
    }
}

async function updateEstagio(estagioId) {
  if (estagioId === oportunidade.value.estagio) return
  
  if (!confirm(`Deseja mover para o estágio "${estagios.value.find(e => e.id === estagioId)?.nome}"?`)) return
  
  try {
    await api.patch(`/oportunidades/${oportunidade.value.id}/`, { estagio: estagioId })
    oportunidade.value.estagio = estagioId
  } catch (error) {
    alert('Erro ao mudar estágio.')
  }
}

async function handleDelete() {
  if (!confirm('Tem certeza que deseja EXCLUIR este negócio? Esta ação não pode ser desfeita.')) return
  
  try {
    await api.delete(`/oportunidades/${oportunidade.value.id}/`)
    router.push('/kanban')
  } catch (error) {
    alert('Erro ao excluir negócio.')
  }
}

// Helpers de UI
function getEstagioColor(estagio) {
  if (estagio.id === oportunidade.value?.estagio) return estagio.cor
  return '#e5e7eb' // Gray-200
}

function getEstagioClass(estagio) {
   if (estagio.id === oportunidade.value?.estagio) return 'opacity-100 scale-110 z-10'
   return 'opacity-60 hover:opacity-100'
}

function formatPhoneLocal(field) {
  let val = contactForm.value[field] || ''
  let digits = val.replace(/\D/g, '')
  if (digits.length > 11) digits = digits.slice(0, 11)
  
  if (digits.length === 0) {
    contactForm.value[field] = ''
  } else if (digits.length <= 2) {
    contactForm.value[field] = `(${digits}`
  } else if (digits.length <= 6) {
    contactForm.value[field] = `(${digits.slice(0,2)}) ${digits.slice(2)}`
  } else if (digits.length <= 10) {
    contactForm.value[field] = `(${digits.slice(0,2)}) ${digits.slice(2,6)}-${digits.slice(6)}`
  } else {
    contactForm.value[field] = `(${digits.slice(0,2)}) ${digits.slice(2,7)}-${digits.slice(7)}`
  }
}

function formatPhone(phone) {
  if (!phone) return ''
  return phone.replace(/(\d{2})(\d{1})(\d{4})(\d{4})/, '($1) $2 $3-$4')
}

// Navegar para detalhe do contato
function goToContactDetail() {
  if (oportunidade.value.contato_principal) {
    router.push(`/contatos/${oportunidade.value.contato_principal}`)
  }
}

// Modais Contato/Empresa
// NOTA: Se já tem entidade vinculada, abre para EDIÇÃO. Se não, abre NOVO.
function openContactModal() {
  if (oportunidade.value.contatos_detalhe?.length) {
    selectedContato.value = oportunidade.value.contatos_detalhe[0]
  } else {
    selectedContato.value = null
  }
  showContactModal.value = true
}

function closeContactModal() {
  showContactModal.value = false
  selectedContato.value = null
}

function openCompanyModal() {
  if (oportunidade.value.empresas_detalhe?.length) {
    selectedCompany.value = oportunidade.value.empresas_detalhe[0]
  } else {
    selectedCompany.value = null
  }
  showCompanyModal.value = true
}

function closeCompanyModal() {
  showCompanyModal.value = false
  selectedCompany.value = null
}

function openWhatsapp() {
   const phone = oportunidade.value.contato_telefone
   if (!phone) return alert('Sem telefone para WhatsApp')
   
   whatsappData.value = {
     number: phone,
     title: oportunidade.value.contato_nome
   }
   showWhatsappChat.value = true
}

async function refreshData() {
  await loadData()
}

function handleTimelineAction(action) {
  if (action === 'whatsapp') {
    openWhatsapp()
    return
  }
  initialTipoAtividade.value = action === 'note' ? 'NOTA' : 'TAREFA'
  showAtividadeModal.value = true
}

function handleAtividadeSaved() {
  showAtividadeModal.value = false
  timelineFeedRef.value?.refresh()
  refreshData()
}
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-bold text-sm uppercase tracking-wider transition-all active:scale-95 flex items-center justify-center;
}
.btn-primary {
  @apply bg-primary-600 text-white hover:bg-primary-700;
}
.btn-white {
  @apply bg-white border hover:bg-gray-50;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
