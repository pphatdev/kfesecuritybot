<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-(--text-heading) tracking-tight">Announcements</h1>
        <p class="text-sm text-(--text-muted) mt-1">Broadcast messages to your monitored groups, channels, and private users.</p>
      </div>
    </div>

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
    <div v-if="activeTab === 'send' || activeTab === 'schedule'">
      <form @submit.prevent="sendAnnouncement" class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Left Column: Compose Message -->
        <div class="lg:col-span-8 space-y-6">
          <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
                <IconMessageDots class="w-5 h-5 text-primary" />
                Compose Message
              </h2>
            </div>

            <!-- Media Upload (Compact Chat UX Style) -->
            <div class="space-y-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Attachment</span>
                  <span class="text-[10px] text-(--text-muted) opacity-80">(Optional, Max 50MB)</span>
                </div>
                
                <!-- Compact Attachment Trigger Button (Only if no file attached) -->
                <button 
                  v-if="!attachedFile"
                  type="button" 
                  @click="triggerFileInput"
                  class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-500/5 hover:bg-slate-500/10 border border-(--border-color) rounded-lg text-xs font-semibold text-(--text-body) transition-all cursor-pointer shadow-sm hover:text-primary"
                >
                  <IconPaperclip class="w-3.5 h-3.5 text-primary" />
                  <span>Attach Media</span>
                </button>
              </div>
              
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileChange" 
                class="hidden" 
                accept="image/*,video/*,application/pdf,application/zip,.doc,.docx,.xls,.xlsx"
              />

              <!-- Compact Media Preview State -->
              <div v-if="attachedFile" class="flex items-center gap-3 bg-slate-500/5 border border-(--border-color) rounded-lg p-2.5 w-fit max-w-full">
                <!-- Thumbnail -->
                <div class="w-10 h-10 rounded-md bg-primary-subtle text-primary flex items-center justify-center shrink-0 overflow-hidden border border-(--border-color)">
                  <img v-if="attachedFile.type.startsWith('image/') && previewUrl" :src="previewUrl" class="w-full h-full object-cover" />
                  <IconMovie v-else-if="attachedFile.type.startsWith('video/')" class="w-5 h-5" />
                  <IconFileDescription v-else class="w-5 h-5" />
                </div>
                
                <!-- Info -->
                <div class="flex flex-col min-w-0 pr-1 text-xs">
                  <span class="font-semibold text-(--text-heading) truncate max-w-[150px] sm:max-w-[250px]">{{ attachedFile.name }}</span>
                  <span class="text-(--text-muted) font-mono opacity-80 mt-0.5">{{ formatFileSize(attachedFile.size) }}</span>
                </div>
                
                <!-- Crop Button (Only for images) -->
                <button 
                  v-if="attachedFile.type.startsWith('image/')"
                  type="button" 
                  @click="openCropModal" 
                  class="w-6 h-6 hover:bg-primary/10 text-(--text-muted) hover:text-primary rounded-full flex items-center justify-center transition-colors cursor-pointer shrink-0"
                  title="Crop Image"
                >
                  <IconScissors class="w-4 h-4" />
                </button>

                <!-- Remove Button -->
                <button 
                  type="button" 
                  @click.prevent="removeFile" 
                  class="w-6 h-6 hover:bg-danger/10 text-(--text-muted) hover:text-danger rounded-full flex items-center justify-center transition-colors cursor-pointer shrink-0"
                  title="Remove attachment"
                >
                  <IconX class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Textarea -->
            <div class="mt-6 border-t border-(--border-color) pt-5 space-y-2">
              <label for="message" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Message Body</label>
              <textarea 
                id="message" 
                v-model="message" 
                rows="8"
                placeholder="Enter your announcement here... HTML formatting (<b>, <i>, <a>, <code>) is fully supported."
                class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg px-4 py-3 text-sm text-(--text-body) placeholder:text-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all shadow-inner"
                :required="!attachedFile"
              ></textarea>
              <div class="flex justify-between items-center text-xs text-(--text-muted) px-1">
                <span>Supports Telegram HTML syntax</span>
                <span :class="{'text-danger font-medium': message.length > 4000}">{{ message.length }} / 4000</span>
              </div>
            </div>

            <!-- DateTime / Cron Picker (Only in Schedule Tab) -->
            <div v-if="activeTab === 'schedule'" class="mt-6 border-t border-(--border-color) pt-5 space-y-4">
              <!-- Schedule Type Toggle -->
              <div class="flex items-center gap-4 bg-slate-500/5 px-4 py-2 rounded-lg border border-(--border-color) w-fit">
                <label class="flex items-center gap-2 text-xs font-bold text-(--text-body) uppercase tracking-wider cursor-pointer">
                  <input type="radio" v-model="scheduleType" value="once" class="text-primary focus:ring-primary focus:ring-offset-0 bg-transparent border-(--border-color)" />
                  One-time
                </label>
                <label class="flex items-center gap-2 text-xs font-bold text-(--text-body) uppercase tracking-wider cursor-pointer">
                  <input type="radio" v-model="scheduleType" value="recurring" class="text-primary focus:ring-primary focus:ring-offset-0 bg-transparent border-(--border-color)" />
                  Recurring (Cron)
                </label>
              </div>

              <!-- One-time Datepicker -->
              <div v-if="scheduleType === 'once'" class="space-y-2">
                <label class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Scheduled Time</label>
                
                <div class="relative w-full" ref="pickerContainer">
                  <!-- Trigger Button -->
                  <button 
                    type="button" 
                    @click="toggleDropdown"
                    class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg px-4 py-2.5 text-sm text-(--text-body) text-left focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all flex items-center justify-between shadow-inner cursor-pointer"
                  >
                    <div class="flex items-center gap-2">
                      <IconCalendarClock class="w-4 h-4 text-primary" />
                      <span :class="{'text-(--text-muted)': !scheduleTime}">
                        {{ formattedScheduleTime || 'Select date & time' }}
                      </span>
                    </div>
                    <IconChevronDown class="w-4 h-4 text-(--text-muted) transition-transform duration-200" :class="{'rotate-180': isDropdownOpen}" />
                  </button>
                  
                  <!-- Popover Dropdown overlay panel -->
                  <div 
                    v-if="isDropdownOpen" 
                    class="absolute left-0 mt-2 z-30 bg-(--bg-card) border border-(--border-color) rounded-2xl shadow-(--shadow-lg) p-4 w-[340px] select-none text-left animate-fade-in"
                  >
                    <!-- Month & Year Selector Header -->
                    <div class="flex items-center justify-between pb-3 border-b border-(--border-color) mb-3">
                      <button 
                        type="button" 
                        @click="prevMonth" 
                        class="p-1 hover:bg-slate-500/10 rounded-lg text-(--text-muted) hover:text-(--text-heading) transition-colors cursor-pointer"
                      >
                        <IconChevronLeft class="w-4 h-4" />
                      </button>
                      <span class="text-sm font-semibold text-(--text-heading)">
                        {{ monthNames[currentMonth] }} {{ currentYear }}
                      </span>
                      <button 
                        type="button" 
                        @click="nextMonth" 
                        class="p-1 hover:bg-slate-500/10 rounded-lg text-(--text-muted) hover:text-(--text-heading) transition-colors cursor-pointer"
                      >
                        <IconChevronRight class="w-4 h-4" />
                      </button>
                    </div>
                    
                    <!-- Week Days Headers -->
                    <div class="grid grid-cols-7 gap-1 text-center text-[10px] font-bold text-(--text-muted) uppercase tracking-wider mb-2">
                      <span>Su</span>
                      <span>Mo</span>
                      <span>Tu</span>
                      <span>We</span>
                      <span>Th</span>
                      <span>Fr</span>
                      <span>Sa</span>
                    </div>
                    
                    <!-- Calendar Day Cells -->
                    <div class="grid grid-cols-7 gap-1 text-center">
                      <div v-for="(cell, idx) in calendarCells" :key="idx" class="aspect-square flex items-center justify-center">
                        <span v-if="cell.type === 'empty'" class="w-8 h-8"></span>
                        <button
                          type="button"
                          @click="selectDay(cell)"
                          :disabled="cell.disabled"
                          class="w-8 h-8 rounded-lg text-xs font-semibold flex items-center justify-center transition-all cursor-pointer"
                          :class="[
                            isSameDay(cell.date, selectedDate)
                              ? 'bg-primary text-white shadow-sm font-bold'
                              : cell.disabled
                                ? 'opacity-25 cursor-not-allowed text-(--text-muted)'
                                : 'text-(--text-body) hover:bg-slate-500/10 hover:text-(--text-heading)'
                          ]"
                        >
                          {{ cell.day }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Time Picker Section -->
                    <div class="flex items-center justify-between border-t border-(--border-color) pt-3 mt-3">
                      <span class="text-xs font-bold text-(--text-muted) uppercase tracking-wider">Time</span>
                      <div class="flex items-center gap-1.5 bg-slate-500/5 px-2.5 py-1 rounded-xl border border-(--border-color)">
                        <!-- Hour Selector Dropdown -->
                        <select 
                          v-model="selectedHour" 
                          @change="updateScheduleTime" 
                          class="bg-transparent border-none text-sm text-(--text-heading) font-semibold focus:ring-0 p-0 text-center w-8 cursor-pointer appearance-none outline-none font-mono"
                        >
                          <option v-for="h in 12" :key="h" :value="h" class="bg-(--bg-card) text-(--text-heading)">{{ String(h).padStart(2, '0') }}</option>
                        </select>
                        
                        <span class="text-(--text-muted) font-semibold">:</span>
                        
                        <!-- Minute Selector Dropdown -->
                        <select 
                          v-model="selectedMinute" 
                          @change="updateScheduleTime" 
                          class="bg-transparent border-none text-sm text-(--text-heading) font-semibold focus:ring-0 p-0 text-center w-8 cursor-pointer appearance-none outline-none font-mono"
                        >
                          <option v-for="m in 60" :key="m-1" :value="m-1" class="bg-(--bg-card) text-(--text-heading)">{{ String(m-1).padStart(2, '0') }}</option>
                        </select>
                        
                        <!-- AM/PM Toggle Segment -->
                        <div class="flex border-l border-(--border-color) pl-2 ml-1 gap-1">
                          <button 
                            type="button" 
                            @click="selectedAmPm = 'AM'; updateScheduleTime()"
                            class="px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all cursor-pointer"
                            :class="selectedAmPm === 'AM' ? 'bg-primary text-white shadow-sm' : 'text-(--text-muted) hover:text-(--text-heading)'"
                          >
                            AM
                          </button>
                          <button 
                            type="button" 
                            @click="selectedAmPm = 'PM'; updateScheduleTime()"
                            class="px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all cursor-pointer"
                            :class="selectedAmPm === 'PM' ? 'bg-primary text-white shadow-sm' : 'text-(--text-muted) hover:text-(--text-heading)'"
                          >
                            PM
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Dropdown Action Footer -->
                    <div class="flex justify-end mt-3 pt-2 border-t border-(--border-color)">
                      <button 
                        type="button" 
                        @click="isDropdownOpen = false" 
                        class="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold hover:bg-primary-hover shadow-sm transition-colors cursor-pointer"
                      >
                        Apply
                      </button>
                    </div>
                  </div>
                </div>
                <p class="text-xs text-(--text-muted)">The announcement will be queued and sent automatically at this local time.</p>
              </div>

              <!-- Recurring Cron Expression Input -->
              <div v-else class="space-y-3">
                <div class="space-y-2">
                  <label for="cron" class="block text-xs font-semibold text-(--text-muted) uppercase tracking-wider">Cron Expression</label>
                  <input 
                    id="cron" 
                    type="text" 
                    v-model="cronExpression" 
                    placeholder="e.g. */30 * * * * or 0 9 * * 1"
                    class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg px-4 py-2.5 text-sm text-(--text-body) placeholder:text-(--text-muted) focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all shadow-inner"
                    required
                  />
                  <!-- Active Cron Description Badge -->
                  <div v-if="cronExpression.trim()" class="flex items-center gap-1.5 text-xs text-primary font-semibold bg-primary-subtle/50 px-2.5 py-1.5 rounded-lg border border-primary/20 w-fit">
                    <IconCheck class="w-3.5 h-3.5 shrink-0" />
                    <span>Active Schedule: {{ activeCronDescription }}</span>
                  </div>
                </div>

                <!-- Cron Templates -->
                <div class="bg-slate-500/5 border border-(--border-color) rounded-lg p-3 space-y-2">
                  <span class="block text-[10px] font-bold text-(--text-muted) uppercase tracking-wider">Quick-Select Cron Templates</span>
                  <div class="flex flex-wrap gap-1.5">
                    <button 
                      v-for="tpl in cronTemplates" 
                      :key="tpl.label"
                      type="button" 
                      @click="cronExpression = tpl.expr"
                      class="px-2.5 py-1 border rounded text-[11px] font-semibold transition-all cursor-pointer shadow-sm"
                      :class="cronExpression.trim() === tpl.expr ? 'bg-primary border-primary text-white hover:bg-primary-hover hover:text-white shadow-md' : 'bg-(--bg-card) border-(--border-color) text-(--text-body) hover:bg-slate-500/10 hover:text-(--text-heading)'"
                      :title="tpl.expr"
                    >
                      {{ tpl.label }}
                    </button>
                  </div>
                </div>

                <div class="text-xs text-(--text-muted) space-y-1 mt-1 leading-relaxed">
                  <p>Format: <code>minute hour day-of-month month day-of-week</code> (5 space-separated values).</p>
                  <p>Examples: <code>0 9 * * 1</code> (Every Monday at 9:00 AM) or <code>0 0 * * *</code> (Daily at midnight).</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Select Recipients & Actions -->
        <div class="lg:col-span-4 space-y-6">
          
          <!-- Templates Card -->
          <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5">
            <h2 class="text-xs font-bold text-(--text-muted) uppercase tracking-wider mb-3">
              Announcement Templates
            </h2>
            <div class="flex flex-col gap-2">
              <button 
                v-for="tpl in announcementTemplates" 
                :key="tpl.name"
                type="button" 
                @click="applyTemplate(tpl.text)"
                class="w-full px-3 py-2 bg-slate-500/5 hover:bg-slate-500/10 border border-(--border-color) rounded-lg text-xs font-semibold text-(--text-body) hover:text-(--text-heading) transition-all flex items-center gap-2 cursor-pointer shadow-sm"
              >
                <component :is="tpl.icon" class="w-4 h-4 text-primary shrink-0" />
                {{ tpl.name }}
              </button>
            </div>
          </div>

          <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) flex flex-col h-[500px]">
            <div class="p-5 border-b border-(--border-color) shrink-0">
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-lg font-semibold text-(--text-heading) flex items-center gap-2">
                  <IconUsers class="w-5 h-5 text-primary" />
                  Recipients
                </h2>
                <span class="bg-primary-subtle text-primary text-xs font-bold px-2 py-0.5 rounded-full">
                  {{ selectedGroups.length }} Selected
                </span>
              </div>

              <!-- Search / Filter -->
              <div class="relative">
                <IconSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-(--text-muted)" />
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Search recipients..." 
                  class="w-full bg-(--bg-layout) border border-(--border-color) rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                />
              </div>
            </div>

            <!-- Recipient List -->
            <div class="flex-1 overflow-y-auto p-2">
              <div v-if="pending" class="flex flex-col items-center justify-center h-full text-(--text-muted)">
                <IconLoader class="w-6 h-6 animate-spin mb-2" />
                <span class="text-sm">Loading...</span>
              </div>
              
              <div v-else-if="filteredGroups.length === 0" class="flex flex-col items-center justify-center h-full text-(--text-muted) px-4 text-center">
                <IconGhost class="w-8 h-8 mb-2 opacity-50" />
                <span class="text-sm">{{ searchQuery ? 'No recipients found.' : 'No recipients tracked yet.' }}</span>
              </div>

              <div v-else class="space-y-1">
                <label 
                  v-for="group in filteredGroups" 
                  :key="group.id"
                  class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-(--bg-layout) group/item"
                  :class="{'bg-primary-subtle/30': selectedGroups.includes(group.id)}"
                >
                  <div class="relative flex items-center justify-center">
                    <input 
                      type="checkbox" 
                      :value="group.id" 
                      v-model="selectedGroups"
                      class="peer sr-only"
                    />
                    <div class="w-5 h-5 rounded border-2 border-(--border-color) peer-checked:bg-primary peer-checked:border-primary flex items-center justify-center transition-colors">
                      <IconCheck class="w-3.5 h-3.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" stroke-width="3" />
                    </div>
                  </div>
                  
                  <div class="flex flex-col overflow-hidden flex-1">
                    <span class="text-sm font-medium text-(--text-heading) truncate group-hover/item:text-primary transition-colors">{{ group.title }}</span>
                    <div class="flex items-center gap-2 mt-0.5">
                      <span class="text-[10px] font-bold tracking-widest uppercase" :class="group.type === 'Private Chat' ? 'text-blue-500' : 'text-emerald-500'">
                        {{ group.type }}
                      </span>
                      <span class="text-xs text-(--text-muted) truncate font-mono opacity-60">{{ group.id }}</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
            
            <div class="p-4 border-t border-(--border-color) bg-(--bg-layout)/50 shrink-0">
               <button type="button" @click="toggleSelectAll" class="w-full py-2 text-sm font-semibold text-(--text-heading) hover:bg-(--bg-layout) border border-(--border-color) rounded-lg transition-colors">
                  {{ allFilteredSelected ? 'Deselect All Shown' : 'Select All Shown' }}
                </button>
            </div>
          </div>

          <!-- Action Card -->
          <div class="bg-(--bg-card) border border-(--border-color) rounded-xl shadow-(--shadow-sm) p-5">
             <button 
                type="submit" 
                :disabled="sending || (!message.trim() && !attachedFile) || selectedGroups.length === 0 || (activeTab === 'schedule' && ((scheduleType === 'once' && !scheduleTime) || (scheduleType === 'recurring' && !cronExpression.trim())))"
                class="w-full py-3.5 bg-primary text-white text-sm font-bold rounded-lg hover:bg-primary-hover focus:ring-4 focus:ring-primary/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-md hover:shadow-lg disabled:shadow-none"
              >
                <IconSend v-if="!sending && activeTab === 'send'" class="w-5 h-5" />
                <IconCalendarClock v-else-if="!sending && activeTab === 'schedule'" class="w-5 h-5" />
                <IconLoader v-else class="w-5 h-5 animate-spin" />
                {{ sending ? (activeTab === 'schedule' ? 'Scheduling...' : 'Broadcasting...') : (activeTab === 'schedule' ? 'Schedule Broadcast' : 'Send Broadcast') }}
              </button>
              <p class="text-[11px] text-center text-(--text-muted) mt-3 leading-relaxed">
                <span v-if="activeTab === 'schedule'">
                  Message will be queued to send to <b>{{ selectedGroups.length }}</b> recipients at the scheduled time.
                </span>
                <span v-else>
                  Message will be immediately dispatched to <b>{{ selectedGroups.length }}</b> recipients. This action cannot be undone.
                </span>
              </p>
          </div>

        </div>
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
                <span class="font-medium text-(--text-heading)" :title="schedule.message">{{ truncateText(schedule.message, 60) }}</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
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
  IconScissors
} from '@tabler/icons-vue'

const message = ref('')
const selectedGroups = ref([])
const searchQuery = ref('')
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
}

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

const filteredGroups = computed(() => {
  if (!searchQuery.value.trim()) return groups.value
  const query = searchQuery.value.toLowerCase()
  return groups.value.filter(g => 
    g.title.toLowerCase().includes(query) || 
    g.id.toString().includes(query) ||
    g.type.toLowerCase().includes(query)
  )
})

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
  if (message.value.trim() || selectedGroups.value.length > 0) {
    const confirmed = await showConfirmModal(
      'Load Selected Message?',
      'Loading this message will overwrite your current composer draft (message content and selected recipients). Do you want to proceed?',
      'warning'
    )
    if (!confirmed) return
  }
  
  message.value = schedule.message || ''
  
  if (schedule.chatIds && Array.isArray(schedule.chatIds)) {
    const availableGroupIds = groups.value.map(g => g.id.toString())
    selectedGroups.value = schedule.chatIds
      .map(id => id.toString())
      .filter(id => availableGroupIds.includes(id))
  } else {
    selectedGroups.value = []
  }
  
  router.push({ query: { tab: 'send' } })
  success.value = 'Message and recipients loaded into the composer.'
  error.value = ''
}

const sendAnnouncement = async () => {
  if ((!message.value.trim() && !attachedFile.value) || selectedGroups.value.length === 0) return
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
    if (attachedFile.value) {
      formData.append('file', attachedFile.value)
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
        message.value = ''
        selectedGroups.value = []
        scheduleTime.value = ''
        attachedFile.value = null
        if (previewUrl.value) {
          URL.revokeObjectURL(previewUrl.value)
          previewUrl.value = null
        }
        success.value = 'Announcement successfully scheduled.'
        router.push({ query: { tab: 'queue' } })
        await fetchSchedules()
      }
    } else {
      const res = await $fetch('/api/announce', {
        method: 'POST',
        body: formData
      })
      
      if (res.success) {
        message.value = ''
        selectedGroups.value = []
        attachedFile.value = null
        if (previewUrl.value) {
          URL.revokeObjectURL(previewUrl.value)
          previewUrl.value = null
        }
        success.value = `Successfully broadcasted to ${res.sent} recipient(s).`
        if (res.failed > 0) {
          success.value += ` Failed to send to ${res.failed} recipient(s).`
        }
      }
    }
  } catch (err) {
    error.value = err.data?.statusMessage || err.message || 'An error occurred while sending the broadcast.'
  } finally {
    sending.value = false
  }
}
</script>
