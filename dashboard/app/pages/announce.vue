<template>
  <div class="mx-auto space-y-6">
    <!-- Header -->
    <!-- <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-heading) tracking-tight">Announcements</h1>
        <p class="text-sm text-(--text-muted) mt-1">Broadcast messages to your monitored groups, channels, and private users.</p>
      </div>
    </div> -->

    <!-- Error / Success Banners -->
    <div v-if="error" class="bg-danger-subtle text-danger px-4 py-3 rounded-lg text-sm border border-danger/20 flex items-start gap-3 shadow-sm">
      <IconAlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
      <span>{{ error }}</span>
    </div>
    <div v-if="success" class="bg-success-subtle text-success px-4 py-3 rounded-lg text-sm border border-success/20 flex items-start gap-3 shadow-sm">
      <IconCheck class="w-5 h-5 shrink-0 mt-0.5" />
      <span>{{ success }}</span>
    </div>

    <!-- Tabs Header -->
    <div class="flex flex-wrap gap-2 p-1.5 bg-slate-500/5 rounded-xl border border-(--border-color) w-fit mb-6">
      <NuxtLink 
        :to="{ query: { tab: 'send' } }"
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer"
        :class="[
          activeTab === 'send'
            ? 'bg-primary text-white shadow-sm' 
            : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10'
        ]"
      >
        <IconSend class="w-4 h-4" />
        <span>Send Announcement</span>
      </NuxtLink>
      
      <NuxtLink 
        :to="{ query: { tab: 'schedule' } }"
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer"
        :class="[
          activeTab === 'schedule'
            ? 'bg-primary text-white shadow-sm' 
            : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10'
        ]"
      >
        <IconCalendarClock class="w-4 h-4" />
        <span>Schedule for Later</span>
      </NuxtLink>
      
      <NuxtLink 
        :to="{ query: { tab: 'queue' } }"
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer"
        :class="[
          activeTab === 'queue'
            ? 'bg-primary text-white shadow-sm' 
            : 'text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10'
        ]"
      >
        <IconList class="w-4 h-4" />
        <span>Scheduled Queue</span>
        <span 
          v-if="pendingSchedulesCount > 0" 
          :class="[
            'px-2 py-0.5 rounded-full text-xs font-semibold',
            activeTab === 'queue' ? 'bg-black/20 text-white' : 'bg-slate-500/10 text-(--text-muted)'
          ]"
        >
          {{ pendingSchedulesCount }}
        </span>
      </NuxtLink>
    </div>

    <!-- Compose Announcement (Send / Schedule Tabs) -->
    <div 
      v-if="activeTab === 'send' || activeTab === 'schedule'" 
      :class="isMaximized ? 'fixed inset-0 z-50 bg-[#17212b] h-screen w-screen m-0 p-0' : 'h-[calc(100vh-210px)] min-h-[600px]'"
    >
      <form 
        @submit.prevent="sendAnnouncement" 
        class="flex overflow-hidden h-full bg-[#17212b] relative"
        :class="isMaximized ? 'w-full rounded-none border-none shadow-none' : 'border border-(--border-color) rounded-2xl shadow-xl w-full'"
      >
        
        <!-- Left Pane: Chats/Recipients List -->
        <div 
          class="shrink-0 border-r border-[#101921] flex-col bg-[#17212b]"
          :class="currentMobileView === 'list' ? 'flex w-full md:w-80' : 'hidden md:flex md:w-80'"
        >
          <div class="p-4 border-b border-[#101921] space-y-3 shrink-0">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Recipients</span>
              <span class="bg-primary-subtle text-primary text-[11px] font-bold px-2 py-0.5 rounded-full">
                {{ selectedGroups.length }} Selected
              </span>
            </div>
            <!-- Search / Filter -->
            <div class="relative">
              <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search chats..." 
                class="w-full bg-[#24303f] border border-transparent rounded-lg pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all"
              />
            </div>
            <!-- Mention / Reply Filter Toggle -->
            <div class="flex items-center justify-between pt-1 select-none">
              <label class="flex items-center gap-1.5 cursor-pointer text-[10px] text-slate-400 hover:text-slate-200 transition-colors">
                <input 
                  type="checkbox" 
                  v-model="filterMentionsOnly" 
                  class="rounded bg-[#24303f] border-slate-700 text-primary focus:ring-0 w-3 h-3 cursor-pointer" 
                />
                <span>Show only mentions/replies</span>
              </label>
              <span v-if="mentionsCount > 0" class="text-[9px] font-bold text-yellow-400 bg-yellow-500/10 px-1.5 py-0.5 rounded-full">
                {{ mentionsCount }} chats
              </span>
            </div>
          </div>

          <!-- Recipient List -->
          <div class="flex-1 overflow-y-auto p-2 space-y-1 bg-[#17212b] scrollbar-thin">
            <div v-if="pending" class="flex flex-col items-center justify-center py-12 text-slate-400">
              <IconLoader class="w-5 h-5 animate-spin mb-2" />
              <span class="text-xs">Loading...</span>
            </div>
            
            <div v-else-if="filteredGroups.length === 0" class="flex flex-col items-center justify-center py-12 text-slate-400 px-4 text-center">
              <IconGhost class="w-7 h-7 mb-2 opacity-50" />
              <span class="text-xs">{{ (searchQuery || filterMentionsOnly) ? 'No chats found matching criteria.' : 'No chats tracked.' }}</span>
            </div>

            <div v-else class="space-y-0.5">
              <label 
                v-for="group in filteredGroups" 
                :key="group.id"
                class="flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition-all hover:bg-[#202b36] group/item"
                :class="{'bg-[#2b5278]/40 hover:bg-[#2b5278]/55': selectedGroups.includes(group.id.toString()) || selectedGroups.includes(group.id)}"
              >
                <div class="relative flex items-center justify-center">
                  <input 
                    type="checkbox" 
                    :value="group.id.toString()" 
                    v-model="selectedGroups"
                    class="peer sr-only"
                  />
                  <div class="w-4 h-4 rounded border border-slate-600 peer-checked:bg-primary peer-checked:border-primary flex items-center justify-center transition-colors">
                    <IconCheck class="w-3 h-3 text-white opacity-0 peer-checked:opacity-100 transition-opacity" stroke-width="3" />
                  </div>
                </div>

                <!-- Avatar Gradient sphere -->
                <div class="w-9 h-9 rounded-full bg-gradient-to-tr text-white font-bold flex items-center justify-center shadow-sm text-xs shrink-0 select-none border border-white/5 uppercase" :class="getAvatarColorClass(group.title)">
                  {{ group.title ? group.title.charAt(0) : 'G' }}
                </div>
                
                <!-- Chat Row Info -->
                <div class="flex-1 min-w-0 text-left">
                  <div class="flex items-baseline justify-between gap-1">
                    <span class="text-xs font-semibold text-slate-100 truncate group-hover/item:text-blue-400 transition-colors">{{ group.title }}</span>
                    <span v-if="group.last_message" class="text-[9px] text-slate-500 font-mono shrink-0">{{ group.last_message.time }}</span>
                  </div>
                  <!-- Last message preview text line -->
                  <div class="text-[10px] text-slate-400 truncate mt-0.5" v-if="group.last_message">
                    <span class="font-semibold text-blue-400">{{ group.last_message.sender }}:</span> {{ stripHtml(group.last_message.text) }}
                  </div>
                  <div class="flex items-center gap-1.5 mt-1 flex-wrap">
                    <span class="text-[9px] font-bold tracking-wider uppercase px-1 rounded-sm" :class="group.type === 'Private Chat' ? 'text-blue-400 bg-blue-500/10' : 'text-emerald-400 bg-emerald-500/10'">
                      {{ group.type }}
                    </span>
                    <span v-if="group.has_mention_or_reply" class="text-[9px] font-bold text-yellow-400 bg-yellow-500/10 px-1 rounded-sm shrink-0" title="Bot was mentioned or replied to in this chat">
                      💬 Mentioned
                    </span>
                    <span class="text-[9px] text-slate-500 truncate font-mono">{{ group.id }}</span>
                  </div>
                </div>
              </label>
            </div>
          </div>
          
          <div class="p-3 border-t border-[#101921] bg-[#17212b] shrink-0">
             <button type="button" @click="toggleSelectAll" class="w-full py-2 text-xs font-semibold text-slate-300 hover:text-white bg-[#202b36] hover:bg-[#24303f] border border-slate-700/50 rounded-lg transition-colors cursor-pointer">
                {{ allFilteredSelected ? 'Deselect All Shown' : 'Select All Shown' }}
              </button>
          </div>
        </div>

        <!-- Center Pane: Chat Workspace (The Telegram Chat Room) -->
        <div class="flex-1 flex flex-col chat-bg-pattern relative overflow-hidden">
          
          <!-- Telegram Chat Header -->
          <template v-if="selectedGroups.length > 0">
            <div class="px-5 py-3.5 backdrop-blur-md bg-[#17212b]/85 border-b border-[#101921]/80 flex items-center justify-between shrink-0 select-none z-10">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-gradient-to-tr text-white font-bold flex items-center justify-center shadow-sm text-xs shrink-0 select-none border border-white/5 uppercase" :class="getAvatarColorClass(previewChatTitle)">
                  {{ previewChatTitle ? previewChatTitle.charAt(0) : '📢' }}
                </div>
                <div class="text-left">
                  <h4 class="text-xs font-semibold text-white leading-tight">
                    {{ previewChatTitle }}
                  </h4>
                  <span class="text-[10px] text-blue-400 font-medium leading-none block mt-1">
                    {{ previewChatSub }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-3 text-slate-400">
                <button 
                  type="button" 
                  @click="isMaximized = !isMaximized"
                  class="p-1 hover:bg-slate-500/10 rounded-lg transition-colors cursor-pointer text-slate-400 hover:text-white"
                  :title="isMaximized ? 'Minimize screen' : 'Maximize screen'"
                >
                  <IconArrowsMinimize class="w-4 h-4" v-if="isMaximized" />
                  <IconArrowsMaximize class="w-4 h-4" v-else />
                </button>
                <button 
                  type="button" 
                  @click="showRightSidebar = !showRightSidebar"
                  class="p-1 hover:bg-slate-500/10 rounded-lg transition-colors cursor-pointer text-slate-400 hover:text-white"
                  title="Toggle Broadcast settings panel"
                  :class="{'text-primary bg-primary-subtle/20 hover:text-primary': showRightSidebar}"
                >
                  <IconInfoCircle class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Chat Messages Area (Scrollable Message History) -->
            <div ref="chatScrollContainer" class="flex-1 p-6 relative flex flex-col justify-start overflow-y-auto select-none scrollbar-thin">
              
              <!-- Chat Bubbles Area -->
              <div class="space-y-4 mb-4 flex-1">
                <!-- Loading Indicator -->
                <div v-if="loadingHistory && chatHistory.length === 0" class="flex justify-center items-center py-8 text-slate-400">
                  <IconLoader class="w-5 h-5 animate-spin mr-2" />
                  <span class="text-xs">Loading chat history...</span>
                </div>

                <!-- Empty state for this specific chat -->
                <div v-else-if="chatHistory.length === 0" class="text-center py-8 text-[11px] text-slate-500 italic">
                  No recent messages recorded for this chat.
                </div>

                <!-- Message History list bubbles -->
                <div 
                  v-for="msg in chatHistory" 
                  :key="msg.message_id" 
                  class="flex items-start gap-3 w-full mx-auto text-left"
                  :class="msg.is_bot ? 'flex-row-reverse text-right' : 'flex-row'"
                >
                  <!-- Avatar -->
                  <div 
                    class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm text-xs border animate-fade-in"
                    :class="msg.is_bot ? 'bg-primary text-white border-primary/20' : 'bg-slate-700 text-slate-100 border-slate-600'"
                  >
                    {{ msg.is_bot ? '🤖' : (msg.sender ? msg.sender.charAt(0).toUpperCase() : '👤') }}
                  </div>

                  <!-- Bubble Wrapper -->
                  <div class="flex-1 space-y-1 min-w-0" :class="{'text-right': msg.is_bot}">
                    <div class="flex items-baseline gap-1.5" :class="{'justify-end': msg.is_bot}">
                      <span class="text-[11px] font-semibold" :class="msg.is_bot ? 'text-blue-400' : 'text-slate-300'">
                        {{ msg.sender }}
                      </span>
                      <span v-if="msg.is_bot" class="text-[8px] text-slate-500 font-medium">bot</span>
                    </div>

                    <!-- Bubble Body -->
                    <div 
                      class="border rounded-2xl p-3 shadow-md text-xs relative max-w-md inline-block text-left"
                      :class="[
                        msg.is_bot 
                          ? 'bg-[#17212b] border-[#2b5278]/20 text-slate-100 rounded-tr-none' 
                          : 'bg-[#182533] border-slate-700/30 text-slate-200 rounded-tl-none',
                        msg.is_deleted ? 'opacity-60 italic bg-red-950/20 border-red-500/20' : ''
                      ]"
                    >
                      <!-- Deleted Banner -->
                      <div v-if="msg.is_deleted" class="text-red-400 flex items-center gap-1.5">
                        <IconAlertCircle class="w-3.5 h-3.5 shrink-0" />
                        <span>Removed: {{ msg.delete_reason || 'moderated' }}</span>
                      </div>
                      
                      <div v-else>
                        <!-- Sticker render -->
                        <div v-if="msg.sticker_id" class="w-[120px] h-[120px] flex items-center justify-center py-1 relative">
                          <img v-if="msg.sticker_thumb_id" :src="`/api/stickers/image?file_id=${msg.sticker_thumb_id}`" class="w-full h-full object-contain pointer-events-none" @error="$event.target.style.display='none'" />
                          <lottie-player v-else-if="msg.is_animated" :src="`/api/stickers/image.json?file_id=${msg.sticker_id}`" autoplay loop background="transparent" style="width: 100%; height: 100%;"></lottie-player>
                          <video v-else-if="msg.is_video" :src="`/api/stickers/image?file_id=${msg.sticker_id}`" autoplay loop muted playsinline class="w-full h-full object-contain"></video>
                          
                          <!-- Dynamic fallback cascade for old messages -->
                          <template v-else>
                            <img v-if="!failedStickerTypes[msg.message_id]" :src="`/api/stickers/image?file_id=${msg.sticker_id}`" class="w-full h-full object-contain pointer-events-none" @error="handleStickerImageError(msg.message_id)" />
                            <video v-else-if="failedStickerTypes[msg.message_id] === 'video'" :src="`/api/stickers/image?file_id=${msg.sticker_id}`" autoplay loop muted playsinline class="w-full h-full object-contain" @error="handleStickerVideoError(msg.message_id)"></video>
                            <lottie-player v-else-if="failedStickerTypes[msg.message_id] === 'lottie'" :src="`/api/stickers/image.json?file_id=${msg.sticker_id}`" autoplay loop background="transparent" style="width: 100%; height: 100%;"></lottie-player>
                          </template>
                        </div>
                        
                        <!-- Media file attachment placeholder -->
                        <div v-else-if="msg.media_type" class="mb-1.5 rounded-lg overflow-hidden border border-slate-700/40 p-2 bg-black/15 flex items-center gap-2 max-w-[240px]">
                          <IconMovie class="w-4 h-4 text-primary shrink-0" v-if="msg.media_type === 'video'" />
                          <IconPhoto class="w-4 h-4 text-primary shrink-0" v-else-if="msg.media_type === 'photo'" />
                          <IconFileDescription class="w-4 h-4 text-primary shrink-0" v-else />
                          <div class="flex flex-col min-w-0 text-[10px] text-left">
                            <span class="font-semibold text-slate-300 truncate">{{ msg.media_name || 'Attachment' }}</span>
                          </div>
                        </div>

                        <!-- Main text -->
                        <div v-if="msg.text" v-html="msg.text" class="wrap-break-word leading-relaxed select-text pr-1"></div>
                      </div>

                      <div class="text-[8px] text-slate-500 mt-1 text-right font-mono select-none">
                        {{ msg.time }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <!-- Bottom Composer Input Bar (The Telegram Input area) -->
            <div class="p-4 backdrop-blur-md bg-[#17212b]/85 border-t border-[#101921]/80 shrink-0 flex items-center gap-3 select-none z-10">
              
              <!-- Attachment & Emoji Input Container -->
              <div class="flex-1 bg-[#182533] border border-slate-700/20 rounded-2xl px-3 py-2 flex items-center gap-2.5 shadow-inner">
                <!-- Attach Media trigger -->
                <button 
                  type="button" 
                  @click="triggerFileInput"
                  class="w-8 h-8 rounded-full hover:bg-slate-500/10 text-slate-400 hover:text-primary flex items-center justify-center transition-colors cursor-pointer shrink-0"
                  title="Attach Photo/Video/Document"
                >
                  <IconPaperclip class="w-4 h-4" />
                </button>
                
                <input 
                  type="file" 
                  ref="fileInput" 
                  @change="handleFileChange" 
                  class="hidden" 
                  accept="image/*,video/*,application/pdf,application/zip,.doc,.docx,.xls,.xlsx"
                />

                <!-- Text Composer Textarea -->
                <textarea 
                  v-if="composeMode === 'text'"
                  v-model="message"
                  rows="1"
                  placeholder="Write a message... Supports HTML tags."
                  class="flex-1 bg-transparent border-none text-slate-100 placeholder-slate-400 focus:ring-0 focus:outline-none m-0 text-sm max-h-80 min-h-[20px] resize-none leading-relaxed"
                  @keydown.enter.exact.prevent="sendAnnouncement"
                  style="field-sizing: content;"
                ></textarea>

                <!-- Sticker composer active state info -->
                <div v-else class="flex-1 flex items-center h-8 text-xs text-slate-400">
                  <span class="italic" v-if="selectedStickerId">Sticker selected. Ready to send.</span>
                  <span class="italic text-slate-500" v-else>Pick a sticker from the drawer below...</span>
                </div>

                <!-- Smiley Toggle Button -->
                <button 
                  type="button" 
                  @click="composeMode = (composeMode === 'text' ? 'sticker' : 'text')"
                  class="w-8 h-8 rounded-full hover:bg-slate-500/10 flex items-center justify-center transition-colors cursor-pointer shrink-0"
                  :class="composeMode === 'sticker' ? 'text-primary bg-primary-subtle/20' : 'text-slate-400 hover:text-primary'"
                  title="Toggle Stickers Panel"
                >
                  <IconMoodSmile class="w-4 h-4" />
                </button>
              </div>

              <!-- Send Circular Button -->
              <button 
                type="submit" 
                :disabled="sending || (composeMode === 'text' ? (!message.trim() && !attachedFile) : !selectedStickerId) || selectedGroups.length === 0 || (activeTab === 'schedule' && ((scheduleType === 'once' && !scheduleTime) || (scheduleType === 'recurring' && !cronExpression.trim())))"
                class="w-9 h-9 rounded-full bg-primary text-white hover:bg-primary-hover flex items-center justify-center shadow-md hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-all shrink-0"
                :title="activeTab === 'schedule' ? 'Schedule Broadcast' : 'Send Broadcast'"
              >
                <IconLoader v-if="sending" class="w-4.5 h-4.5 animate-spin" />
                <IconCalendarClock v-else-if="activeTab === 'schedule'" class="w-4.5 h-4.5" />
                <IconSend v-else class="w-4.5 h-4.5" />
              </button>
            </div>

            <!-- Attachment preview overlay chip in the chat middle pane -->
            <div v-if="attachedFile" class="absolute bottom-20 left-4 bg-[#182533] border border-slate-700/50 rounded-xl p-2 flex items-center gap-2 max-w-[280px] shadow-lg animate-fade-in">
              <div class="w-8 h-8 rounded bg-primary-subtle text-primary flex items-center justify-center overflow-hidden shrink-0 border border-slate-700">
                <img v-if="attachedFile.type.startsWith('image/') && previewUrl" :src="previewUrl" class="w-full h-full object-cover" />
                <IconMovie v-else-if="attachedFile.type.startsWith('video/')" class="w-4 h-4" />
                <IconFileDescription v-else class="w-4 h-4" />
              </div>
              <div class="flex flex-col min-w-0 text-[10px]">
                <span class="font-semibold text-slate-200 truncate">{{ attachedFile.name }}</span>
                <span class="text-slate-500 font-mono">{{ formatFileSize(attachedFile.size) }}</span>
              </div>
              <button type="button" @click="removeFile" class="w-4.5 h-4.5 rounded-full bg-black/25 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer">
                <IconX class="w-3 h-3" />
              </button>
            </div>

            <!-- Sticker Keyboard Popover (Drawer inside central workspace) -->
            <Transition
              enter-active-class="transition duration-200 ease-out transform"
              enter-from-class="translate-y-full"
              enter-to-class="translate-y-0"
              leave-active-class="transition duration-150 ease-in transform"
              leave-from-class="translate-y-0"
              leave-to-class="translate-y-full"
            >
              <div v-if="composeMode === 'sticker'" class="absolute bottom-16 inset-x-0 bg-[#17212b] border-t border-[#101921] h-[340px] flex flex-col z-[20] shadow-2xl animate-in">
                <div class="p-3 border-b border-[#101921] flex gap-2 shrink-0 select-none">
                  <!-- Mini search for sticker sets -->
                  <div class="relative flex-1">
                    <IconSearch class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-400" />
                    <input 
                      type="text" 
                      v-model="searchPackName" 
                      placeholder="Search sticker packs..." 
                      class="w-full bg-[#24303f] border border-transparent rounded-lg pl-8 pr-4 py-1 text-[11px] text-slate-100 placeholder-slate-400 focus:outline-none"
                      @keyup.enter="loadStickerPack(searchPackName)"
                    />
                  </div>
                  <button 
                    type="button" 
                    @click="loadStickerPack(searchPackName)"
                    :disabled="loadingStickers || !searchPackName.trim()"
                    class="px-2.5 py-1 bg-primary text-white rounded-lg text-[10px] font-semibold disabled:opacity-50 cursor-pointer"
                  >
                    <IconLoader v-if="loadingStickers" class="w-3.5 h-3.5 animate-spin" />
                    <span v-else>Load</span>
                  </button>
                </div>

                <!-- Popular Packs selection chips -->
                <div class="px-3 py-1.5 border-b border-[#101921]/50 bg-[#17212b] flex items-center gap-1.5 overflow-x-auto shrink-0 select-none scrollbar-none">
                  <span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider shrink-0">Popular:</span>
                  <button 
                    v-for="pack in ['Animals', 'tg_placeholders', 'CherryHot', 'MochaBull', 'EggDog', 'Diggy']" 
                    :key="pack"
                    type="button"
                    @click="searchPackName = pack; loadStickerPack(pack)"
                    class="text-[9px] bg-[#202b36] hover:bg-primary/20 hover:text-primary text-slate-300 border border-slate-700/40 rounded-full px-2.5 py-0.5 transition-all cursor-pointer shrink-0"
                  >
                    {{ pack }}
                  </button>
                </div>

                <!-- Loaded Stickers Grid list -->
                <div class="flex-1 overflow-y-auto p-3 bg-[#0e1621] scrollbar-thin select-none">
                  <div v-if="stickerError" class="bg-danger-subtle text-danger px-3 py-2 rounded-lg text-[11px] border border-danger/10 text-left">
                    {{ stickerError }}
                  </div>
                  <div v-else-if="loadedStickers.length === 0" class="flex flex-col items-center justify-center h-full text-slate-500 py-12">
                    <IconMoodSmile class="w-8 h-8 opacity-40 mb-1.5" />
                    <span class="text-[11px]">Select a popular pack or type a name to load.</span>
                  </div>
                  <div v-else class="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-9 gap-2">
                    <div 
                      v-for="stk in loadedStickers" 
                      :key="stk.file_id"
                      @click="selectSticker(stk)"
                      class="group relative flex items-center justify-center p-1.5 rounded-lg bg-[#182533] hover:bg-[#202b36] border border-slate-700/50 cursor-pointer transition-all aspect-square overflow-hidden hover:scale-105"
                      :class="{'border-2 border-primary ring-2 ring-primary/20': selectedStickerId === stk.file_id}"
                    >
                      <div class="w-full h-full relative flex items-center justify-center">
                        <img v-if="stk.thumbnail?.file_id || stk.thumb?.file_id" :src="`/api/stickers/image?file_id=${stk.thumbnail?.file_id || stk.thumb?.file_id}`" class="w-full h-full object-contain pointer-events-none" loading="lazy" @error="$event.target.style.display='none'" />
                        <lottie-player v-else-if="stk.is_animated" :src="`/api/stickers/image.json?file_id=${stk.file_id}`" autoplay loop background="transparent" style="width: 100%; height: 100%;"></lottie-player>
                        <video v-else-if="stk.is_video" :src="`/api/stickers/image?file_id=${stk.file_id}`" autoplay loop muted playsinline class="w-full h-full object-contain"></video>
                        <img v-else :src="`/api/stickers/image?file_id=${stk.file_id}`" class="w-full h-full object-contain pointer-events-none" loading="lazy" @error="$event.target.style.display='none'" />
                        
                        <div v-if="stk.is_animated || stk.is_video" class="absolute bottom-0.5 right-0.5 bg-black/70 text-slate-200 text-[7px] px-1 py-0.5 rounded uppercase font-bold tracking-wider shadow-sm backdrop-blur-sm z-10 pointer-events-none">
                          {{ stk.is_animated ? 'Animated' : 'Video' }}
                        </div>
                      </div>
                      <div v-if="selectedStickerId === stk.file_id" class="absolute top-0.5 right-0.5 w-3.5 h-3.5 rounded-full bg-primary text-white flex items-center justify-center shadow z-20">
                        <IconCheck class="w-2 h-2" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </template>

          <div v-else class="flex-1 flex flex-col items-center justify-center p-8 text-center select-none bg-[#0e1621] h-full animate-fade-in">
            <div class="w-16 h-16 rounded-full bg-slate-500/5 flex items-center justify-center mb-4 border border-slate-700/10">
              <IconMessageDots class="w-8 h-8 text-primary opacity-60" />
            </div>
            <h3 class="text-sm font-bold text-slate-300">Select a recipient to start messaging</h3>
            <p class="text-[11px] text-slate-500 mt-1.5 max-w-xs leading-normal">Choose one or more groups, channels, or private chats from the list on the left to start composing and broadcasting your announcements.</p>
          </div>

        </div>

        <!-- Right Pane: Broadcast Tools Drawer (Telegram Chat Info Pane style) -->
          <Transition
          enter-active-class="transition duration-200 ease-out transform"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition duration-150 ease-in transform"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div v-show="showRightSidebar" class="w-80 shrink-0 border-l border-[#101921] flex flex-col bg-[#17212b] overflow-y-auto p-4 space-y-5 select-none scrollbar-thin">
          <div class="flex items-center justify-between pb-3 border-b border-[#101921] shrink-0">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Info & Settings</span>
              <button type="button" @click="showRightSidebar = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-500/10 cursor-pointer">
                <IconX class="w-4 h-4" />
              </button>
            </div>

            <!-- Active Profile Info -->
            <div v-if="activeGroup" class="flex flex-col items-center bg-[#202b36] p-4 rounded-xl border border-slate-700/30 text-center relative overflow-hidden shrink-0">
              <div class="absolute inset-x-0 top-0 h-10 bg-linear-to-r from-primary/20 to-blue-500/10"></div>
              <div class="w-16 h-16 rounded-full bg-linear-to-tr text-white font-bold flex items-center justify-center shadow-lg text-xl select-none border-2 border-[#17212b] z-[10] uppercase mt-2 mb-3" :class="getAvatarColorClass(activeGroup.title)">
                {{ activeGroup.title ? activeGroup.title.charAt(0) : 'G' }}
              </div>
              <h3 class="text-sm font-bold text-slate-100 truncate w-full">{{ activeGroup.title }}</h3>
              <p class="text-[10px] text-slate-400 font-mono mt-1 mb-2">{{ activeGroup.id }}</p>
              <div class="flex items-center justify-center gap-2 flex-wrap">
                <span class="text-[9px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-sm" :class="activeGroup.type === 'Private Chat' ? 'text-blue-400 bg-blue-500/10' : 'text-emerald-400 bg-emerald-500/10'">
                  {{ activeGroup.type }}
                </span>
                <span v-if="activeGroup.has_mention_or_reply" class="text-[9px] font-bold text-yellow-400 bg-yellow-500/10 px-2 py-0.5 rounded-sm" title="Bot was mentioned or replied to in this chat">
                  💬 Mentioned
                </span>
              </div>
            </div>

            <!-- Scheduler settings section -->
            <div class="space-y-2 bg-[#202b36] p-3 rounded-xl border border-slate-700/30">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider">Schedule Delivery</span>
                <!-- Badge for schedule type -->
                <span class="text-[9px] bg-primary/20 text-primary font-bold px-1.5 py-0.5 rounded uppercase font-mono">
                  {{ activeTab === 'schedule' ? 'Scheduled' : 'Instant' }}
                </span>
              </div>
              
              <div v-if="activeTab === 'schedule'" class="space-y-3 pt-2">
                <!-- One-time vs Recurring toggle -->
                <div class="flex gap-2 bg-[#17212b] p-1 rounded-lg border border-slate-800">
                  <button 
                    type="button" 
                    @click="scheduleType = 'once'"
                    class="flex-1 py-1 rounded text-[10px] font-bold transition-all cursor-pointer"
                    :class="scheduleType === 'once' ? 'bg-primary text-white' : 'text-slate-400 hover:text-slate-200'"
                  >
                    Once
                  </button>
                  <button 
                    type="button" 
                    @click="scheduleType = 'recurring'"
                    class="flex-1 py-1 rounded text-[10px] font-bold transition-all cursor-pointer"
                    :class="scheduleType === 'recurring' ? 'bg-primary text-white' : 'text-slate-400 hover:text-slate-200'"
                  >
                    Recurring
                  </button>
                </div>

                <!-- One-time inputs -->
                <div v-if="scheduleType === 'once'" class="space-y-1.5 relative" ref="pickerContainer">
                  <label class="block text-[9px] font-bold text-slate-400 uppercase">Send Time</label>
                  <button 
                    type="button" 
                    @click="toggleDropdown"
                    class="w-full bg-[#17212b] border border-slate-700/50 rounded-lg px-3 py-2 text-xs text-slate-100 flex items-center justify-between cursor-pointer"
                  >
                    <span class="truncate">{{ formattedScheduleTime || 'Select date & time' }}</span>
                    <IconChevronDown class="w-3.5 h-3.5 text-slate-400" />
                  </button>
                  
                  <!-- Datepicker dropdown popover -->
                  <div v-if="isDropdownOpen" class="absolute right-0 bottom-full mb-2 z-[30] bg-[#17212b] border border-[#101921] rounded-xl p-3 w-[260px] shadow-2xl animate-fade-in text-[11px]">
                    <div class="flex items-center justify-between pb-2 border-b border-[#101921] mb-2">
                      <button type="button" @click="prevMonth" class="text-slate-400 hover:text-white cursor-pointer"><IconChevronLeft class="w-3.5 h-3.5" /></button>
                      <span class="font-bold text-slate-200">{{ monthNames[currentMonth] }} {{ currentYear }}</span>
                      <button type="button" @click="nextMonth" class="text-slate-400 hover:text-white cursor-pointer"><IconChevronRight class="w-3.5 h-3.5" /></button>
                    </div>
                    <div class="grid grid-cols-7 gap-1 text-center font-bold text-slate-500 mb-1">
                      <div v-for="d in ['Su','Mo','Tu','We','Th','Fr','Sa']" :key="d" class="text-[9px]">{{ d }}</div>
                    </div>
                    <div class="grid grid-cols-7 gap-1 text-center">
                      <div v-for="(cell, cIdx) in calendarCells" :key="cIdx" class="aspect-square flex items-center justify-center">
                        <button 
                          v-if="cell.type === 'day'"
                          type="button"
                          @click="selectDay(cell)"
                          :disabled="cell.disabled"
                          class="w-full h-full rounded text-[10px] font-semibold transition-all cursor-pointer"
                          :class="[
                            cell.disabled ? 'text-slate-600 cursor-not-allowed' : 'text-slate-200 hover:bg-[#2b5278]/30',
                            selectedDate && isSameDay(cell.date, selectedDate) ? 'bg-primary text-white font-bold' : ''
                          ]"
                        >
                          {{ cell.day }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Hours/Minutes selector -->
                    <div class="flex items-center justify-between pt-2 border-t border-[#101921] mt-2 gap-1 select-none">
                      <div class="flex items-center gap-1 bg-[#202b36] px-1.5 py-0.5 rounded border border-slate-700/30">
                        <select v-model="selectedHour" @change="updateScheduleTime" class="bg-transparent border-none text-[10px] text-slate-200 font-semibold focus:ring-0 p-0 outline-none cursor-pointer">
                          <option v-for="h in 12" :key="h" :value="h" class="bg-[#17212b] text-slate-200">{{ h }}</option>
                        </select>
                        <span class="text-slate-500 font-bold">:</span>
                        <select v-model="selectedMinute" @change="updateScheduleTime" class="bg-transparent border-none text-[10px] text-slate-200 font-semibold focus:ring-0 p-0 outline-none cursor-pointer">
                          <option v-for="m in 60" :key="m-1" :value="m-1" class="bg-[#17212b] text-slate-200">{{ String(m-1).padStart(2, '0') }}</option>
                        </select>
                        <div class="flex border-l border-slate-700/50 pl-1.5 ml-1 gap-1">
                          <button type="button" @click="selectedAmPm = 'AM'; updateScheduleTime()" class="px-1 py-0.2 rounded text-[8px] font-bold" :class="selectedAmPm === 'AM' ? 'bg-primary text-white' : 'text-slate-500'">AM</button>
                          <button type="button" @click="selectedAmPm = 'PM'; updateScheduleTime()" class="px-1 py-0.2 rounded text-[8px] font-bold" :class="selectedAmPm === 'PM' ? 'bg-primary text-white' : 'text-slate-500'">PM</button>
                        </div>
                      </div>
                      <button type="button" @click="isDropdownOpen = false" class="px-2 py-1 bg-primary text-white rounded text-[9px] font-bold cursor-pointer">Apply</button>
                    </div>
                  </div>
                </div>

                <!-- Recurring Cron inputs -->
                <div v-else class="space-y-2">
                  <label for="cron" class="block text-[9px] font-bold text-slate-400 uppercase">Cron Expression</label>
                  <input 
                    id="cron" 
                    type="text" 
                    v-model="cronExpression" 
                    placeholder="e.g. */30 * * * *"
                    class="w-full bg-[#17212b] border border-slate-700/50 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none"
                    required
                  />
                  <!-- Cron Templates -->
                  <div class="flex flex-wrap gap-1">
                    <button 
                      v-for="tpl in cronTemplates" 
                      :key="tpl.label"
                      type="button" 
                      @click="cronExpression = tpl.expr"
                      class="px-2 py-0.5 border rounded-full text-[9px] font-semibold transition-all cursor-pointer"
                      :class="cronExpression.trim() === tpl.expr ? 'bg-primary border-primary text-white' : 'bg-[#17212b] border-slate-700/30 text-slate-400 hover:text-slate-200'"
                    >
                      {{ tpl.label }}
                    </button>
                  </div>
                </div>
              </div>
              <div v-else class="text-[10px] text-slate-400 pt-1 leading-normal">
                Message will be broadcasted immediately to all checked recipients.
              </div>
            </div>

            <!-- Inline Buttons builder section -->
            <div v-if="composeMode === 'text'" class="space-y-2.5 bg-[#202b36] p-3 rounded-xl border border-slate-700/30">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider">Keyboard Buttons</span>
                <!-- Switch -->
                <button 
                  type="button"
                  @click="hasButtons = !hasButtons"
                  class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
                  :class="hasButtons ? 'bg-primary' : 'bg-slate-700'"
                >
                  <span class="pointer-events-none inline-block h-3.8 w-3.8 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="hasButtons ? 'translate-x-4' : 'translate-x-0'" />
                </button>
              </div>

              <div v-if="hasButtons" class="space-y-2 pt-1.5">
                <div v-for="(btn, index) in buttons" :key="index" class="flex flex-col gap-1.5 bg-[#17212b] p-2 rounded-lg border border-slate-800">
                  <div class="flex items-center justify-between">
                    <span class="text-[9px] text-slate-500 font-mono">#{{ index + 1 }}</span>
                    <button type="button" @click="buttons.splice(index, 1)" class="text-danger hover:text-danger/80 cursor-pointer">
                      <IconTrash class="w-3 h-3" />
                    </button>
                  </div>
                  <input 
                    type="text" 
                    v-model="btn.text" 
                    placeholder="Button Label"
                    class="w-full bg-[#24303f] border border-transparent rounded px-2 py-1 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                  <input 
                    type="url" 
                    v-model="btn.url" 
                    placeholder="URL (https://...)"
                    class="w-full bg-[#24303f] border border-transparent rounded px-2 py-1 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
                <button 
                  type="button" 
                  @click="addButton"
                  class="w-full py-1.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/10 rounded-lg text-[10px] font-semibold transition-all cursor-pointer flex items-center justify-center gap-1"
                >
                  <IconPlus class="w-3 h-3" />
                  Add Button
                </button>
              </div>
            </div>

            <!-- Templates Section -->
            <div class="space-y-2.5 bg-[#202b36] p-3 rounded-xl border border-slate-700/30 flex-1 flex flex-col min-h-[220px]">
              <span class="text-[11px] font-bold text-slate-300 uppercase tracking-wider shrink-0">Announcement Templates</span>
              <div class="flex-1 overflow-y-auto space-y-1.5 scrollbar-thin pr-1 text-left">
                <button 
                  v-for="tpl in announcementTemplates" 
                  :key="tpl.name"
                  type="button" 
                  @click="applyTemplate(tpl.text)"
                  class="w-full text-left p-2 bg-[#17212b] hover:bg-[#24303f] border border-slate-800 rounded-lg text-[11px] font-medium text-slate-300 hover:text-white transition-all flex items-center gap-2 cursor-pointer"
                >
                  <component :is="tpl.icon" class="w-3.5 h-3.5 text-primary shrink-0" />
                  <span class="truncate">{{ tpl.name }}</span>
                </button>
              </div>
            </div>

            <!-- Submit Broadcast button (Double confirmation action inside setting drawer) -->
            <div class="pt-2 border-t border-[#101921] shrink-0">
               <button 
                  type="submit" 
                  :disabled="sending || (composeMode === 'text' ? (!message.trim() && !attachedFile) : !selectedStickerId) || selectedGroups.length === 0 || (activeTab === 'schedule' && ((scheduleType === 'once' && !scheduleTime) || (scheduleType === 'recurring' && !cronExpression.trim())))"
                  class="w-full py-3 bg-primary text-white text-xs font-bold rounded-lg hover:bg-primary-hover focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-1.5 shadow-md hover:shadow-lg disabled:shadow-none cursor-pointer"
                >
                  <IconSend v-if="!sending && activeTab === 'send'" class="w-4 h-4" />
                  <IconCalendarClock v-else-if="!sending && activeTab === 'schedule'" class="w-4 h-4" />
                  <IconLoader v-else class="w-4 h-4 animate-spin" />
                  {{ sending ? (activeTab === 'schedule' ? 'Scheduling...' : 'Broadcasting...') : (activeTab === 'schedule' ? 'Schedule Broadcast' : 'Send Broadcast') }}
                </button>
            </div>
            
          </div>
        </Transition>

      </form>
    </div>

    <!-- Scheduled Queue (Queue Tab) -->
    <div v-if="activeTab === 'queue'" class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5 sm:p-6">
      <div class="flex items-center justify-between mb-4 border-b border-(--border-color) pb-4">
        <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
          <IconCalendarClock class="w-5 h-5 text-primary" />
          Scheduled Announcements Queue
        </h2>
        <button 
          type="button" 
          @click="fetchSchedules" 
          class="p-1.5 hover:bg-(--bg-layout) border border-(--border-color) rounded-lg transition-colors text-(--text-muted) hover:text-(--text-heading)"
          title="Refresh Queue"
        >
          <IconRefresh class="w-4 h-4" :class="{'animate-spin': loadingSchedules}" />
        </button>
      </div>

      <!-- Schedules Loader / Empty state -->
      <div v-if="loadingSchedules && schedules.length === 0" class="flex flex-col items-center justify-center py-12 text-(--text-muted)">
        <IconLoader class="w-8 h-8 animate-spin mb-2" />
        <span class="text-sm">Loading queue...</span>
      </div>

      <div v-else-if="schedules.length === 0" class="flex flex-col items-center justify-center py-12 text-(--text-muted) text-center">
        <IconGhost class="w-10 h-10 mb-2 opacity-50 text-slate-400" />
        <span class="text-sm font-medium">No scheduled messages in the queue.</span>
        <p class="text-xs opacity-75 mt-1">Navigate to the "Schedule for Later" tab to compose one.</p>
      </div>

      <!-- Schedules List -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-(--border-color) text-[11px] font-semibold text-(--text-muted) uppercase tracking-wider">
              <th class="py-3 px-4">Message</th>
              <th class="py-3 px-4">Recipients</th>
              <th class="py-3 px-4">Scheduled For</th>
              <th class="py-3 px-4">Status</th>
              <th class="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-(--border-color) text-sm">
            <tr v-for="schedule in sortedSchedules" :key="schedule.id" class="hover:bg-(--bg-layout)/50 transition-colors">
              <td class="py-3.5 px-4 font-normal text-(--text-body) max-w-xs sm:max-w-md truncate">
                <div class="flex flex-col gap-1">
                  <div v-if="schedule.file_type === 'sticker'" class="flex items-center gap-2">
                    <div class="w-12 h-12 rounded-2xl bg-linear-to-r from-primary/20 to-primary-subtle border border-primary/20 flex items-center justify-center shrink-0">
                      <div class="w-8 h-8 rounded-full bg-linear-to-tr from-primary to-blue-400 shadow-inner flex items-center justify-center">
                        <img :src="`/api/stickers/image?file_id=${schedule.sticker_thumb_id || schedule.sticker_id}`" class="w-full h-full object-contain" />
                      </div>
                    </div>
                    <span class="text-xs text-(--text-muted)">Sticker Broadcast</span>
                  </div>
                  <span v-else class="font-medium text-(--text-heading)" :title="schedule.message">{{ truncateText(schedule.message, 60) }}</span>
                  <!-- Display Buttons configured -->
                  <div v-if="schedule.buttons && schedule.buttons.length > 0" class="flex flex-wrap gap-1 mt-1">
                    <span v-for="(btn, bIdx) in schedule.buttons" :key="bIdx" class="text-[10px] text-(--text-muted) inline-flex items-center gap-0.5 bg-slate-500/5 px-1 py-0.5 rounded border border-(--border-color)" :title="btn.url">
                      <IconLink class="w-2.5 h-2.5 text-primary shrink-0" />
                      {{ btn.text }}
                    </span>
                  </div>
                  <span v-else-if="schedule.button_text" class="text-[10px] text-(--text-muted) flex items-center gap-1" :title="schedule.button_url">
                    <IconLink class="w-3 h-3 text-primary shrink-0" />
                    Button: <span class="font-semibold text-(--text-heading)">{{ schedule.button_text }}</span>
                  </span>
                </div>
              </td>
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-1.5">
                  <span class="bg-primary-subtle text-primary text-xs font-semibold px-2 py-0.5 rounded-full">
                    {{ schedule.chatIds.length }} recipient(s)
                  </span>
                </div>
              </td>
              <td class="py-3.5 px-4 font-mono text-xs text-(--text-muted)">
                <div class="flex flex-col gap-1">
                  <span>{{ formatDateTime(schedule.sendAt) || 'Calculating...' }}</span>
                  <span v-if="schedule.cron" class="text-[10px] bg-primary-subtle text-primary border border-primary/20 px-1.5 py-0.5 rounded-lg w-fit inline-flex items-center gap-1" title="Cron Expression">
                    <IconRefresh class="w-3 h-3 animate-spin-slow" />
                    {{ schedule.cron }}
                  </span>
                </div>
              </td>
              <td class="py-3.5 px-4">
                <span :class="getStatusBadgeClass(schedule.status)" class="text-xs font-semibold px-2.5 py-0.5 rounded-full inline-flex items-center gap-1">
                  {{ formatStatus(schedule.status) }}
                </span>
              </td>
              <td class="py-3.5 px-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    type="button"
                    @click="reuseMessage(schedule)"
                    class="text-xs text-primary hover:text-white bg-primary-subtle hover:bg-primary px-2.5 py-1 rounded font-semibold transition-all inline-flex items-center gap-1 cursor-pointer"
                    title="Load message & recipients into composer to edit or resend"
                  >
                    <IconCopy class="w-3.5 h-3.5" />
                    Reuse
                  </button>

                  <button 
                    v-if="schedule.status === 'pending'"
                    type="button"
                    @click="cancelSchedule(schedule.id)"
                    :disabled="cancellingId === schedule.id"
                    class="text-xs text-danger hover:text-white bg-danger-subtle hover:bg-danger/80 px-2.5 py-1 rounded font-semibold disabled:opacity-50 transition-all inline-flex items-center gap-1 cursor-pointer"
                  >
                    <IconTrash class="w-3.5 h-3.5" v-if="cancellingId !== schedule.id" />
                    <IconLoader class="w-3.5 h-3.5 animate-spin" v-else />
                    Cancel
                  </button>
                  <button 
                    v-else
                    type="button"
                    @click="deleteScheduleHistory(schedule.id)"
                    :disabled="cancellingId === schedule.id"
                    class="text-xs text-(--text-muted) hover:text-danger hover:bg-danger-subtle p-1 rounded transition-all cursor-pointer"
                    title="Remove from history"
                  >
                    <IconX class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Custom Confirmation Modal -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="confirmModal.show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
        <div class="bg-(--bg-card) border border-(--border-color) rounded-2xl shadow-(--shadow-lg) max-w-md w-full overflow-hidden p-6 space-y-4 transform scale-100 transition-all">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0" :class="confirmModal.type === 'danger' ? 'bg-danger-subtle text-danger' : 'bg-warning-subtle text-warning'">
              <IconAlertTriangle class="w-5 h-5" v-if="confirmModal.type === 'danger'" />
              <IconAlertCircle class="w-5 h-5" v-else />
            </div>
            <div class="space-y-1 flex-1">
              <h3 class="text-base font-semibold text-(--text-heading)">{{ confirmModal.title }}</h3>
              <p class="text-sm text-(--text-muted) leading-relaxed">{{ confirmModal.message }}</p>
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button 
              type="button" 
              @click="closeConfirmModal(false)"
              class="px-4 py-2 border border-(--border-color) hover:bg-(--bg-layout) rounded-lg text-sm font-semibold text-(--text-body) hover:text-(--text-heading) transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button 
              type="button" 
              @click="closeConfirmModal(true)"
              class="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-all cursor-pointer shadow-md hover:shadow-lg"
              :class="confirmModal.type === 'danger' ? 'bg-danger hover:bg-danger/90' : 'bg-primary hover:bg-primary-hover'"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Cropping Modal -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showCropModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fade-in">
        <div class="bg-(--bg-card) border border-(--border-color) rounded-2xl shadow-(--shadow-lg) max-w-xl w-full overflow-hidden p-6 space-y-4 transform scale-100 transition-all select-none">
          <div class="flex items-center justify-between border-b border-(--border-color) pb-3">
            <h3 class="text-base font-semibold text-(--text-heading) flex items-center gap-2">
              <IconScissors class="w-4 h-4 text-primary" />
              Crop Image
            </h3>
            <button 
              type="button" 
              @click="showCropModal = false" 
              class="text-(--text-muted) hover:text-(--text-heading) hover:bg-slate-500/10 p-1 rounded-lg transition-colors cursor-pointer"
            >
              <IconX class="w-4 h-4" />
            </button>
          </div>

          <!-- Crop Container Workspace -->
          <div class="relative overflow-hidden flex items-center justify-center bg-black/40 rounded-xl border border-(--border-color) min-h-[300px] max-h-[450px]">
            <div ref="cropContainerEl" class="relative max-w-full max-h-full overflow-hidden w-fit">
              <img 
                ref="cropImageEl"
                :src="cropImageSrc" 
                class="object-contain max-h-[400px] select-none pointer-events-none" 
                alt="Image to crop"
              />
              
              <!-- Draggable Crop Box Overlay -->
              <div 
                class="absolute border-2 border-primary cursor-move select-none"
                :style="{
                  left: cropBox.x + '%',
                  top: cropBox.y + '%',
                  width: cropBox.w + '%',
                  height: cropBox.h + '%',
                  boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.65)'
                }"
                @mousedown="startDrag"
              >
                <!-- Grid Lines (Premium Aesthetic) -->
                <div class="absolute inset-0 grid grid-cols-3 grid-rows-3 pointer-events-none opacity-30">
                  <div class="border-b border-dashed border-white"></div>
                  <div class="border-b border-dashed border-white"></div>
                  <div class="border-b border-dashed border-white"></div>
                  <div class="border-r border-dashed border-white"></div>
                  <div class="border-r border-dashed border-white"></div>
                  <div class="border-r border-dashed border-white"></div>
                </div>

                <!-- Resize Handle bottom-right -->
                <div 
                  class="absolute bottom-0 right-0 w-4 h-4 bg-primary border-2 border-white rounded-full translate-x-1/2 translate-y-1/2 cursor-se-resize shadow-md hover:scale-125 transition-transform"
                  @mousedown="startResize"
                ></div>
              </div>
            </div>
          </div>

          <!-- Crop Footer Controls -->
          <div class="flex items-center justify-between pt-2 border-t border-(--border-color)">
            <p class="text-xs text-(--text-muted)">Drag the selection to move; drag the bottom-right dot to resize.</p>
            <div class="flex gap-3">
              <button 
                type="button" 
                @click="showCropModal = false"
                class="px-4 py-2 border border-(--border-color) hover:bg-(--bg-layout) rounded-lg text-xs font-semibold text-(--text-body) hover:text-(--text-heading) transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button 
                type="button" 
                @click="saveCrop"
                class="px-4 py-2 bg-primary text-white rounded-lg text-xs font-bold hover:bg-primary-hover shadow-sm transition-colors cursor-pointer"
              >
                Apply Crop
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Custom Toast Notification -->
    <Transition
      enter-active-class="transition duration-300 ease-out transform"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="toast.show" class="fixed top-5 right-5 z-9999 max-w-sm w-full bg-slate-900/95 border border-slate-700/50 backdrop-blur-md rounded-xl p-4 shadow-2xl flex items-start gap-3 select-none pointer-events-auto">
        <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" :class="toast.type === 'success' ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
          <IconCheck class="w-4 h-4" v-if="toast.type === 'success'" />
          <IconAlertCircle class="w-4 h-4" v-else />
        </div>
        <div class="flex-1 text-xs font-semibold text-slate-100 pt-1.5 leading-normal text-left">
          {{ toast.message }}
        </div>
        <button type="button" @click="toast.show = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-500/10 cursor-pointer">
          <IconX class="w-3.5 h-3.5" />
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  IconAlertCircle, 
  IconCheck, 
  IconLoader, 
  IconSend, 
  IconMessageDots, 
  IconUsers, 
  IconSearch, 
  IconGhost,
  IconCalendarClock,
  IconRefresh,
  IconTrash,
  IconX,
  IconList,
  IconTool,
  IconRocket,
  IconInfoCircle,
  IconAlertTriangle,
  IconChevronLeft,
  IconChevronRight,
  IconChevronDown,
  IconPaperclip,
  IconPhoto,
  IconMovie,
  IconFileDescription,
  IconCopy,
  IconScissors,
  IconLink,
  IconPlus,
  IconMoodSmile,
  IconArrowsMaximize,
  IconArrowsMinimize
} from '@tabler/icons-vue'

const message = ref('')
const selectedGroups = ref([])
const searchQuery = ref('')
const filterMentionsOnly = ref(false)
const hasButtons = ref(false)
const buttons = ref([])
const showRightSidebar = ref(true)
const isMaximized = ref(false)
const currentMobileView = ref('list')

const toast = ref({ show: false, message: '', type: 'success' })
let toastTimeout = null

const triggerToast = (msg, type = 'success') => {
  if (toastTimeout) clearTimeout(toastTimeout)
  toast.value = { show: true, message: msg, type }
  toastTimeout = setTimeout(() => {
    toast.value.show = false
  }, 4000)
}

const chatHistory = ref([])
const loadingHistory = ref(false)
const chatScrollContainer = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScrollContainer.value) {
      chatScrollContainer.value.scrollTop = chatScrollContainer.value.scrollHeight
    }
  })
}

const activeChatId = computed(() => {
  return selectedGroups.value.length > 0 ? selectedGroups.value[0].toString() : null
})

const failedStickerTypes = ref({})

const handleStickerImageError = (msgId) => {
  if (!failedStickerTypes.value[msgId]) {
    failedStickerTypes.value[msgId] = 'video'
  }
}
const handleStickerVideoError = (msgId) => {
  if (failedStickerTypes.value[msgId] === 'video') {
    failedStickerTypes.value[msgId] = 'lottie'
  }
}

const fetchChatHistory = async () => {
  const chatId = activeChatId.value
  if (!chatId) {
    chatHistory.value = []
    return
  }
  loadingHistory.value = true
  try {
    const data = await $fetch('/api/chats/history', {
      query: { chat_id: chatId }
    })
    chatHistory.value = data.history || []
    scrollToBottom()
  } catch (err) {
    console.error('Failed to fetch chat history:', err)
  } finally {
    loadingHistory.value = false
  }
}

watch(activeChatId, (newId) => {
  fetchChatHistory()
  if (newId) {
    currentMobileView.value = 'chat'
  } else {
    currentMobileView.value = 'list'
  }
})

watch(chatHistory, () => {
  scrollToBottom()
}, { deep: true })

const formattedCurrentTime = ref('12:00 PM')

onMounted(() => {
  const updateClock = () => {
    formattedCurrentTime.value = new Date().toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }
  updateClock()
  const interval = setInterval(updateClock, 60000)
  
  fetchChatHistory()
  const historyInterval = setInterval(() => {
    if (activeChatId.value) {
      fetchChatHistory()
    }
  }, 5000)
  
  onBeforeUnmount(() => {
    clearInterval(interval)
    clearInterval(historyInterval)
  })
})

useHead({
  script: [
    {
      src: '/api/lottie-player.js',
      defer: true
    }
  ]
})

const composeMode = ref('text')
const searchPackName = ref('')
const loadedStickers = ref([])
const loadingStickers = ref(false)
const selectedStickerId = ref('')
const selectedStickerRenderId = ref('')
const selectedStickerEmoji = ref('')
const selectedStickerIsAnimated = ref(false)
const selectedStickerIsVideo = ref(false)
const selectedStickerPackName = ref('')
const stickerError = ref('')

const loadStickerPack = async (packName) => {
  if (!packName || !packName.trim()) return
  loadingStickers.value = true
  stickerError.value = ''
  loadedStickers.value = []
  
  try {
    const data = await $fetch('/api/stickers/set', {
      query: { name: packName.trim() }
    })
    if (data.success && data.result) {
      loadedStickers.value = data.result.stickers || []
      selectedStickerPackName.value = data.result.name
      if (loadedStickers.value.length === 0) {
        stickerError.value = 'Sticker pack has no stickers or is empty.'
      }
    } else {
      stickerError.value = 'Sticker pack not found.'
    }
  } catch (err) {
    console.error('Failed to load sticker pack:', err)
    stickerError.value = err.data?.statusMessage || err.message || 'Sticker pack not found or failed to fetch. Ensure the pack name is correct (case-sensitive).'
  } finally {
    loadingStickers.value = false
  }
}

const selectSticker = (sticker) => {
  selectedStickerId.value = sticker.file_id
  selectedStickerRenderId.value = sticker.thumbnail?.file_id || sticker.thumb?.file_id || sticker.file_id
  selectedStickerEmoji.value = sticker.emoji || ''
  selectedStickerIsAnimated.value = sticker.is_animated || false
  selectedStickerIsVideo.value = sticker.is_video || false
}

const renderedMessage = computed(() => {
  if (!message.value) return '<span class="text-slate-400/60 italic">Message body preview...</span>'
  
  let text = message.value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  text = text
    .replace(/&lt;b&gt;([\s\S]*?)&lt;\/b&gt;/gi, '<strong>$1</strong>')
    .replace(/&lt;strong&gt;([\s\S]*?)&lt;\/strong&gt;/gi, '<strong>$1</strong>')
    .replace(/&lt;i&gt;([\s\S]*?)&lt;\/i&gt;/gi, '<em>$1</em>')
    .replace(/&lt;em&gt;([\s\S]*?)&lt;\/em&gt;/gi, '<em>$1</em>')
    .replace(/&lt;u&gt;([\s\S]*?)&lt;\/u&gt;/gi, '<span class="underline">$1</span>')
    .replace(/&lt;s&gt;([\s\S]*?)&lt;\/s&gt;/gi, '<span class="line-through">$1</span>')
    .replace(/&lt;strike&gt;([\s\S]*?)&lt;\/strike&gt;/gi, '<span class="line-through">$1</span>')
    .replace(/&lt;del&gt;([\s\S]*?)&lt;\/del&gt;/gi, '<span class="line-through">$1</span>')
    .replace(/&lt;code&gt;([\s\S]*?)&lt;\/code&gt;/gi, '<code class="bg-black/40 text-pink-400 px-1 py-0.5 rounded font-mono text-xs select-all">$1</code>')
    .replace(/&lt;pre&gt;([\s\S]*?)&lt;\/pre&gt;/gi, '<pre class="bg-black/40 text-pink-400 p-2 rounded font-mono text-xs block overflow-x-auto select-all">$1</pre>')
    .replace(/&lt;a\s+href=&quot;([^&]+)&quot;&gt;([\s\S]*?)&lt;\/a&gt;/gi, '<a href="$1" target="_blank" class="text-blue-400 hover:underline">$2</a>')
    .replace(/&lt;a\s+href=\'([^\']+)\'&gt;([\s\S]*?)&lt;\/a&gt;/gi, '<a href="$1" target="_blank" class="text-blue-400 hover:underline">$2</a>')
    
  return text.replace(/\n/g, '<br>')
})

const addButton = () => {
  buttons.value.push({ text: '', url: '' })
}

const removeButton = (index) => {
  buttons.value.splice(index, 1)
  if (buttons.value.length === 0) {
    hasButtons.value = false
  }
}

watch(hasButtons, (val) => {
  if (val && buttons.value.length === 0) {
    addButton()
  }
})
const error = ref('')
const success = ref('')
const sending = ref(false)
const attachedFile = ref(null)
const previewUrl = ref(null)
const fileInput = ref(null)

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 50 * 1024 * 1024) {
      error.value = 'File size exceeds 50MB limit.'
      attachedFile.value = null
      if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
      previewUrl.value = null
      return
    }
    attachedFile.value = file
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
      previewUrl.value = URL.createObjectURL(file)
    } else {
      previewUrl.value = null
    }
  }
}

const removeFile = () => {
  attachedFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const announcementTemplates = [
  {
    name: 'Schedule Send',
    icon: IconCalendarClock,
    text: '<b>📅 Scheduled Announcement</b>\n\nDear members,\n\nThis is a scheduled message to notify you that:\n\n[Details of the scheduled announcement]\n\nThank you for your attention!\n\nBest regards,\nAdministration Team'
  },
  {
    name: 'Maintenance Notice',
    icon: IconTool,
    text: '<b>🔧 Scheduled Maintenance Notice</b>\n\nDear users,\n\nOur system will undergo scheduled maintenance on <b>[Date]</b> from <b>[Start Time]</b> to <b>[End Time]</b> (UTC).\n\nDuring this period, the bot/services may be temporarily unavailable. We apologize for any inconvenience.\n\nThank you for your understanding!'
  },
  {
    name: 'Feature Release',
    icon: IconRocket,
    text: '<b>🚀 New Feature Update!</b>\n\nWe are excited to announce a new update to our bot!\n\n<b>Key Changes:</b>\n- Feature 1: ...\n- Feature 2: ...\n- Bug fixes and stability improvements.\n\nTry it out now and share your feedback!'
  },
  {
    name: 'Security Alert',
    icon: IconAlertTriangle,
    text: '<b>⚠️ Security Warning</b>\n\nAttention all group members!\n\nPlease be cautious of scammers impersonating admins.\n\nRemember:\n- Admins will <b>never</b> message you first requesting personal details or payments.\n- Always double-check usernames before communicating.\n\nStay safe! 🛡️'
  },
  {
    name: 'General Notice',
    icon: IconInfoCircle,
    text: '<b>📢 Official Announcement</b>\n\nDear members,\n\n[Your announcement text here]\n\nBest regards,\nAdministration Team'
  }
]

const cronTemplates = [
  { label: 'Every 30 Mins', expr: '*/30 * * * *' },
  { label: 'Every Hour', expr: '0 * * * *' },
  { label: 'Daily at 9 AM', expr: '0 9 * * *' },
  { label: 'Daily at Midnight', expr: '0 0 * * *' },
  { label: 'Weekly (Mon 9 AM)', expr: '0 9 * * 1' },
  { label: 'Monthly (1st at Midnight)', expr: '0 0 1 * *' }
]

const confirmModal = ref({
  show: false,
  title: '',
  message: '',
  type: 'warning',
  onConfirm: null
})

const showConfirmModal = (title, message, type = 'warning') => {
  return new Promise((resolve) => {
    confirmModal.value = {
      show: true,
      title,
      message,
      type,
      onConfirm: (result) => {
        confirmModal.value.show = false
        resolve(result)
      }
    }
  })
}

const closeConfirmModal = (result) => {
  if (confirmModal.value.onConfirm) {
    confirmModal.value.onConfirm(result)
  }
}

const isTemplateUsed = ref(false)

const applyTemplate = async (text) => {
  if (message.value.trim()) {
    const confirmed = await showConfirmModal(
      'Overwrite Message Draft?',
      'Applying this template will overwrite your current draft message. Do you want to proceed?',
      'warning'
    )
    if (!confirmed) return
  }
  message.value = text
  isTemplateUsed.value = true
}

watch(message, (newVal) => {
  if (!newVal.trim()) {
    isTemplateUsed.value = false
  }
})

const router = useRouter()
const route = useRoute()

const activeTab = computed(() => route.query.tab || 'send')
const activeCronDescription = computed(() => {
  const expr = cronExpression.value.trim()
  if (!expr) return ''
  const tpl = cronTemplates.find(t => t.expr === expr)
  if (tpl) {
    return `${tpl.label} (${expr})`
  }
  return `Custom (${expr})`
})
const scheduleTime = ref('')
const scheduleType = ref('once')
const cronExpression = ref('')
const loadingSchedules = ref(false)

// Draggable/Resizable Cropper Logic
const showCropModal = ref(false)
const cropImageSrc = ref('')
const cropBox = ref({ x: 15, y: 15, w: 70, h: 70 })
const cropImageEl = ref(null)
const cropContainerEl = ref(null)

const openCropModal = () => {
  if (previewUrl.value) {
    cropImageSrc.value = previewUrl.value
    cropBox.value = { x: 15, y: 15, w: 70, h: 70 }
    showCropModal.value = true
  }
}

let isDragging = false
let isResizing = false
let startMouseX = 0
let startMouseY = 0
let startBoxX = 0
let startBoxY = 0
let startBoxW = 0
let startBoxH = 0

const startDrag = (e) => {
  e.preventDefault()
  isDragging = true
  startMouseX = e.clientX
  startMouseY = e.clientY
  startBoxX = cropBox.value.x
  startBoxY = cropBox.value.y
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDragOrResize)
}

const handleDrag = (e) => {
  if (!isDragging || !cropContainerEl.value) return
  const dx = ((e.clientX - startMouseX) / cropContainerEl.value.clientWidth) * 100
  const dy = ((e.clientY - startMouseY) / cropContainerEl.value.clientHeight) * 100
  
  let newX = startBoxX + dx
  let newY = startBoxY + dy
  
  newX = Math.max(0, Math.min(100 - cropBox.value.w, newX))
  newY = Math.max(0, Math.min(100 - cropBox.value.h, newY))
  
  cropBox.value.x = newX
  cropBox.value.y = newY
}

const startResize = (e) => {
  e.preventDefault()
  e.stopPropagation()
  isResizing = true
  startMouseX = e.clientX
  startMouseY = e.clientY
  startBoxW = cropBox.value.w
  startBoxH = cropBox.value.h
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopDragOrResize)
}

const handleResize = (e) => {
  if (!isResizing || !cropContainerEl.value) return
  const dw = ((e.clientX - startMouseX) / cropContainerEl.value.clientWidth) * 100
  const dh = ((e.clientY - startMouseY) / cropContainerEl.value.clientHeight) * 100
  
  let newW = startBoxW + dw
  let newH = startBoxH + dh
  
  newW = Math.max(10, Math.min(100 - cropBox.value.x, newW))
  newH = Math.max(10, Math.min(100 - cropBox.value.y, newH))
  
  cropBox.value.w = newW
  cropBox.value.h = newH
}

const stopDragOrResize = () => {
  isDragging = false
  isResizing = false
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopDragOrResize)
}

const saveCrop = () => {
  const img = cropImageEl.value
  if (!img) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  const naturalWidth = img.naturalWidth
  const naturalHeight = img.naturalHeight
  
  const sx = (cropBox.value.x / 100) * naturalWidth
  const sy = (cropBox.value.y / 100) * naturalHeight
  const sw = (cropBox.value.w / 100) * naturalWidth
  const sh = (cropBox.value.h / 100) * naturalHeight
  
  canvas.width = sw
  canvas.height = sh
  
  ctx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh)
  
  canvas.toBlob((blob) => {
    if (!blob) return
    
    const croppedFile = new File([blob], attachedFile.value.name, {
      type: attachedFile.value.type || 'image/jpeg',
      lastModified: Date.now()
    })
    
    attachedFile.value = croppedFile
    
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = URL.createObjectURL(croppedFile)
    
    showCropModal.value = false
  }, attachedFile.value.type || 'image/jpeg', 0.95)
}
const schedules = ref([])
const cancellingId = ref('')

// Custom DateTime Picker State
const isDropdownOpen = ref(false)
const pickerContainer = ref(null)
const selectedDate = ref(null)
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())
const selectedHour = ref(12)
const selectedMinute = ref(0)
const selectedAmPm = ref('AM')

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const isSameDay = (d1, d2) => {
  if (!d1 || !d2) return false
  return d1.getFullYear() === d2.getFullYear() &&
         d1.getMonth() === d2.getMonth() &&
         d1.getDate() === d2.getDate()
}

const daysInMonth = (year, month) => {
  return new Date(year, month + 1, 0).getDate()
}

const startDayOfWeek = (year, month) => {
  return new Date(year, month, 1).getDay()
}

const isPastDate = (date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date < today
}

const calendarCells = computed(() => {
  const cells = []
  const startDay = startDayOfWeek(currentYear.value, currentMonth.value)
  const totalDays = daysInMonth(currentYear.value, currentMonth.value)
  
  // Add empty spacer cells for days of previous month
  for (let i = 0; i < startDay; i++) {
    cells.push({ type: 'empty', label: '' })
  }
  
  // Add current month days
  for (let day = 1; day <= totalDays; day++) {
    const dateObj = new Date(currentYear.value, currentMonth.value, day)
    const isDisabled = isPastDate(dateObj)
    cells.push({
      type: 'day',
      day,
      date: dateObj,
      disabled: isDisabled
    })
  }
  return cells
})

const updateScheduleTime = () => {
  if (!selectedDate.value) return
  const hours24 = selectedAmPm.value === 'PM' 
    ? (selectedHour.value === 12 ? 12 : selectedHour.value + 12) 
    : (selectedHour.value === 12 ? 0 : selectedHour.value)
    
  const dateCopy = new Date(selectedDate.value)
  dateCopy.setHours(hours24)
  dateCopy.setMinutes(selectedMinute.value)
  dateCopy.setSeconds(0)
  dateCopy.setMilliseconds(0)
  
  scheduleTime.value = dateCopy.toISOString()
}

const initPickerValues = () => {
  let date = new Date()
  
  // Set default to current time + 1 hour, rounded to 5 minutes
  date.setHours(date.getHours() + 1)
  const remainder = date.getMinutes() % 5
  if (remainder !== 0) {
    date.setMinutes(date.getMinutes() + (5 - remainder))
  }
  
  selectedDate.value = date
  currentYear.value = date.getFullYear()
  currentMonth.value = date.getMonth()
  
  let hours = date.getHours()
  selectedAmPm.value = hours >= 12 ? 'PM' : 'AM'
  selectedHour.value = hours % 12
  if (selectedHour.value === 0) selectedHour.value = 12
  selectedMinute.value = date.getMinutes()
  
  updateScheduleTime()
}

const formattedScheduleTime = computed(() => {
  if (!scheduleTime.value) return ''
  const date = new Date(scheduleTime.value)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
})

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
  if (isDropdownOpen.value && !selectedDate.value) {
    initPickerValues()
  }
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const selectDay = (cell) => {
  if (cell.disabled) return
  selectedDate.value = cell.date
  updateScheduleTime()
}

const handleClickOutside = (event) => {
  if (pickerContainer.value && !pickerContainer.value.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'schedule' && !scheduleTime.value) {
    initPickerValues()
  }
}, { immediate: true })

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

const { data, pending, refresh } = await useFetch('/api/groups')

const groups = computed(() => {
  return data.value?.groups || []
})

const previewChatTitle = computed(() => {
  if (selectedGroups.value.length === 0) return 'Telegram Broadcast'
  const firstGroup = groups.value.find(g => g.id.toString() === selectedGroups.value[0].toString() || g.id === selectedGroups.value[0])
  const title = firstGroup ? firstGroup.title : 'Telegram Broadcast'
  if (selectedGroups.value.length > 1) {
    return `${title} (+${selectedGroups.value.length - 1} others)`
  }
  return title
})

const previewChatSub = computed(() => {
  if (selectedGroups.value.length === 0) return 'broadcast channel'
  const count = selectedGroups.value.length
  return count === 1 ? (activeGroup.value?.type || 'Private Chat') : `${count} recipients`
})

const activeGroup = computed(() => {
  if (selectedGroups.value.length === 1) {
    return groups.value.find(g => g.id.toString() === selectedGroups.value[0].toString() || g.id === selectedGroups.value[0])
  }
  return null
})

const pendingSchedulesCount = computed(() => {
  return schedules.value.filter(s => s.status === 'pending').length
})

const minDateTime = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
})

const mentionsCount = computed(() => {
  return groups.value.filter(g => g.has_mention_or_reply).length
})

const filteredGroups = computed(() => {
  let list = groups.value
  if (filterMentionsOnly.value) {
    list = list.filter(g => g.has_mention_or_reply)
  }
  if (!searchQuery.value.trim()) return list
  const query = searchQuery.value.toLowerCase()
  return list.filter(g => 
    g.title.toLowerCase().includes(query) || 
    g.id.toString().includes(query) ||
    g.type.toLowerCase().includes(query)
  )
})

const getAvatarColorClass = (title) => {
  if (!title) return 'from-blue-500 to-indigo-500'
  const colors = [
    'from-red-500 to-orange-500',
    'from-orange-500 to-yellow-500',
    'from-green-500 to-emerald-500',
    'from-teal-500 to-cyan-500',
    'from-blue-500 to-indigo-500',
    'from-purple-500 to-pink-500',
    'from-pink-500 to-rose-500'
  ]
  let hash = 0
  for (let i = 0; i < title.length; i++) {
    hash = title.charCodeAt(i) + ((hash << 5) - hash)
  }
  const index = Math.abs(hash) % colors.length
  return colors[index]
}

const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '')
}


const allFilteredSelected = computed(() => {
  if (filteredGroups.value.length === 0) return false
  return filteredGroups.value.every(g => selectedGroups.value.includes(g.id))
})

const toggleSelectAll = () => {
  if (allFilteredSelected.value) {
    // Remove all filtered from selected
    const filteredIds = filteredGroups.value.map(g => g.id)
    selectedGroups.value = selectedGroups.value.filter(id => !filteredIds.includes(id))
  } else {
    // Add all filtered to selected
    const current = new Set(selectedGroups.value)
    filteredGroups.value.forEach(g => current.add(g.id))
    selectedGroups.value = Array.from(current)
  }
}

const fetchSchedules = async () => {
  loadingSchedules.value = true
  try {
    const res = await $fetch('/api/schedule')
    schedules.value = res.schedules || []
  } catch (err) {
    console.error('Failed to fetch schedules:', err)
  } finally {
    loadingSchedules.value = false
  }
}

onMounted(() => {
  fetchSchedules()
})

const sortedSchedules = computed(() => {
  return [...schedules.value].sort((a, b) => new Date(a.sendAt) - new Date(b.sendAt))
})

const truncateText = (text, limit) => {
  if (!text) return ''
  if (text.length <= limit) return text
  return text.substring(0, limit) + '...'
}

const formatDateTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleString()
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'pending': return 'badge-soft-warning'
    case 'sending': return 'badge-soft-primary animate-pulse'
    case 'sent': return 'badge-soft-success'
    case 'failed': return 'badge-soft-danger'
    case 'partially_failed': return 'badge-soft-danger'
    default: return 'badge-soft-secondary'
  }
}

const formatStatus = (status) => {
  if (!status) return ''
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
}

const cancelSchedule = async (id) => {
  const confirmed = await showConfirmModal(
    'Cancel Announcement',
    'Are you sure you want to cancel and remove this scheduled announcement? This action cannot be undone.',
    'danger'
  )
  if (!confirmed) return
  
  cancellingId.value = id
  try {
    const res = await $fetch('/api/schedule', {
      method: 'DELETE',
      body: { id }
    })
    if (res.success) {
      success.value = 'Scheduled announcement successfully cancelled.'
      await fetchSchedules()
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'Failed to cancel schedule.'
  } finally {
    cancellingId.value = ''
  }
}

const deleteScheduleHistory = async (id) => {
  cancellingId.value = id
  try {
    const res = await $fetch('/api/schedule', {
      method: 'DELETE',
      body: { id }
    })
    if (res.success) {
      await fetchSchedules()
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'Failed to remove schedule history.'
  } finally {
    cancellingId.value = ''
  }
}

const reuseMessage = async (schedule) => {
  const hasDraft = message.value.trim() || selectedGroups.value.length > 0 || selectedStickerId.value;
  if (hasDraft) {
    const confirmed = await showConfirmModal(
      'Load Selected Message?',
      'Loading this message will overwrite your current composer draft (message content and selected recipients). Do you want to proceed?',
      'warning'
    )
    if (!confirmed) return
  }
  
  if (schedule.file_type === 'sticker' && schedule.sticker_id) {
    composeMode.value = 'sticker'
    selectedStickerId.value = schedule.sticker_id
    selectedStickerRenderId.value = schedule.sticker_thumb_id || schedule.sticker_id
    selectedStickerEmoji.value = ''
    message.value = ''
    loadedStickers.value = []
    stickerError.value = ''
  } else {
    composeMode.value = 'text'
    selectedStickerId.value = ''
    selectedStickerRenderId.value = ''
    selectedStickerEmoji.value = ''
    message.value = schedule.message || ''
  }
  
  if (schedule.buttons && Array.isArray(schedule.buttons) && schedule.buttons.length > 0) {
    hasButtons.value = true
    buttons.value = JSON.parse(JSON.stringify(schedule.buttons))
  } else if (schedule.button_text && schedule.button_url) {
    hasButtons.value = true
    buttons.value = [{ text: schedule.button_text, url: schedule.button_url }]
  } else {
    hasButtons.value = false
    buttons.value = []
  }

  if (schedule.chatIds && Array.isArray(schedule.chatIds)) {
    const availableGroupIds = groups.value.map(g => g.id.toString())
    selectedGroups.value = schedule.chatIds
      .map(id => id.toString())
      .filter(id => availableGroupIds.includes(id))
  } else {
    selectedGroups.value = []
  }
  
  router.push({ query: { tab: 'send' } })
  triggerToast('Message and recipients loaded into the composer.', 'success')
  error.value = ''
}

const sendAnnouncement = async () => {
  if (composeMode.value === 'sticker') {
    if (!selectedStickerId.value || selectedGroups.value.length === 0) return
  } else {
    if ((!message.value.trim() && !attachedFile.value) || selectedGroups.value.length === 0) return
  }
  if (activeTab.value === 'schedule') {
    if (scheduleType.value === 'once' && !scheduleTime.value) return
    if (scheduleType.value === 'recurring' && !cronExpression.value.trim()) return
  }
  
  error.value = ''
  success.value = ''
  sending.value = true
  
  try {
    const formData = new FormData()
    formData.append('message', message.value)
    selectedGroups.value.forEach(id => formData.append('chatIds', id))
    
    if (composeMode.value === 'sticker') {
      formData.append('stickerId', selectedStickerId.value)
      formData.append('stickerThumbId', selectedStickerRenderId.value)
      formData.append('isAnimated', selectedStickerIsAnimated.value)
      formData.append('isVideo', selectedStickerIsVideo.value)
    } else if (attachedFile.value) {
      formData.append('file', attachedFile.value)
    }
    
    if (hasButtons.value && buttons.value.length > 0) {
      const validButtons = buttons.value.filter(b => b.text.trim() && b.url.trim())
      if (validButtons.length > 0) {
        formData.append('buttons', JSON.stringify(validButtons))
      }
    }

    if (activeTab.value === 'schedule') {
      if (scheduleType.value === 'once') {
        const utcString = new Date(scheduleTime.value).toISOString()
        formData.append('sendAt', utcString)
      } else {
        formData.append('cron', cronExpression.value.trim())
      }
      
      const res = await $fetch('/api/schedule', {
        method: 'POST',
        body: formData
      })
      if (res.success) {
        if (!isTemplateUsed.value) {
          message.value = ''
        }
        attachedFile.value = null
        selectedStickerId.value = ''
        selectedStickerRenderId.value = ''
        selectedStickerEmoji.value = ''
        composeMode.value = 'text'
        hasButtons.value = false
        buttons.value = []
        scheduleTime.value = ''
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        if (previewUrl.value) {
          URL.revokeObjectURL(previewUrl.value)
          previewUrl.value = null
        }
        triggerToast('Announcement successfully scheduled.', 'success')
        router.push({ query: { tab: 'queue' } })
        await fetchSchedules()
      }
    } else {
      const res = await $fetch('/api/announce', {
        method: 'POST',
        body: formData
      })
      
      if (res.success) {
        if (!isTemplateUsed.value) {
          message.value = ''
        }
        attachedFile.value = null
        selectedStickerId.value = ''
        selectedStickerRenderId.value = ''
        selectedStickerEmoji.value = ''
        composeMode.value = 'text'
        hasButtons.value = false
        buttons.value = []
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        if (previewUrl.value) {
          URL.revokeObjectURL(previewUrl.value)
          previewUrl.value = null
        }
        let msg = `Successfully broadcasted to ${res.sent} recipient(s).`
        if (res.failed > 0) {
          msg += ` Failed to send to ${res.failed} recipient(s).`
        }
        triggerToast(msg, 'success')
      }
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'An error occurred while sending the broadcast.'
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.chat-bg-pattern {
  background-color: #0e1621;
  background-image: radial-gradient(rgba(43, 82, 120, 0.15) 1.5px, transparent 0), radial-gradient(rgba(43, 82, 120, 0.15) 1.5px, transparent 0);
  background-size: 24px 24px;
  background-position: 0 0, 12px 12px;
}

.scrollbar-thin::-webkit-scrollbar {
  width: 5px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 9999px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
