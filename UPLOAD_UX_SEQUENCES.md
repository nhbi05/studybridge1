# Interactive Upload Flow - Sequence & Wireframes

## Message Sequence Diagram

```
USER                    CurriculumUpload            Zustand Store          ChatInterface
 │                           │                           │                      │
 ├─ Drag file ────────────→  │                           │                      │
 │                           │                           │                      │
 │                           ├─ startAnalysis() ─────→   │                      │
 │                           │                           ├─ setAnalyzing=true   │
 │                           │                           ├─ clearEvents         │
 │                           │                           │                      │
 │                           ├─ addEvent('file_received')→│                      │
 │                           │                           ├─ event: {            │
 │                           │                           │   id, type, message  │
 │                           │                           │   fileName, timestamp│
 │                           │                           │ }                    │
 │                           │                           ├─ useEffect watches ──┤
 │                           │                           │   events array       │
 │                           │                           ├──→ Add to messages   │
 │                           │                           │                      │
 │                           │                        [1500ms delay]            │
 │                           │                           │                      │
 │                           ├─ addEvent('confirming') ──→│                      │
 │                           │                           ├─ useEffect fires    ──┤
 │                           │                        [API call ongoing]        │
 │                           │                           │                      │
 │                           ├─ api.curriculum.upload() ▼                      │
 │                           │ [Backend processes...]                           │
 │                           │ [Extract topics]                                 │
 │                           │ [Run LLM]                                        │
 │ ◄──────────────────────── │ [Return response]                                │
 │                        [2000ms]                       │                      │
 │                           │                           │                      │
 │                           ├─ addEvent('confirmation')→ │                      │
 │                           │   {topics: []}            ├─ Add to messages    ──┤
 │                           │   isAwaitingUserInput: t  │   (marked [System])   │
 │                           │                           │                      │
 │                        [Auto-confirm]                 │                      │
 │                        [2000ms]                       │                      │
 │                           ├─ addEvent('confirmation')→ │                      │
 │                           │   {userResponse: "ok"}    ├─ Add to messages     │
 │                           │                           │                      │
 │                           ├─ setTimeout(1000) ───────→│                      │
 │                           │                           │                      │
 │                           ├─ addEvent('embedding') ───→│                      │
 │                           │                           ├─ Input disabled      │
 │                           │                           ├─ Header shows 🔄     │
 │                           │                           ├─ Auto-scroll ────┤   │
 │                           │                        [1500ms]                  │
 │                           │                           │                      │
 │                           ├─ completeAnalysis() ─────→│                      │
 │                           │   setAnalyzing=false      ├─ Input enabled       │
 │                           │                           │                      │
 │                           ├─ addEvent('complete') ────→│                      │
 │                           │                           ├─ Add final message  ──┤
 │                           │                           │                      │
 │ ◄──────────────────────── ├─ onUploadSuccess() ━━━━━━ │                      │
 │  File processed          │  [Callback to parent]      │                      │
 └                           └                           └                      └
```

---

## Chat Message Timeline (Visual)

```
TIME        CHAT SIDEBAR                           MAIN CONTENT              USER FOCUS
─────────────────────────────────────────────────────────────────────────────────────
 0ms        👋 Welcome message                      Upload area ready         Main area
           (persistent)

 0ms        🤖 Received Math101.pdf!                File marked "Ready"       💫 Chat
           I'm starting deep analysis...

1500ms      🤖 I've identified the                 [no change]               💫 Chat
           primary topics...

2000ms      🤖 I've identified Calculus,            [no change]               💫 Chat
           Linear Algebra, Calculus as 
           goals. Should I include all?
           [System message - yellow]
           💬 Awaiting response...

4000ms      🤖 Got it. Including all 3             [no change]               💫 Chat
           topics in analysis...

5000ms      🤖 Extraction complete!                 Main content blurs        💫 Chat
           Running through BERT model...            "Processing..." overlay   (drawing
           Check Recommendations in 3..2..1 ✨     Input disabled             focus)

6500ms      🤖 Done! I've updated your              Success message          💫 Chat
           curriculum profile with 3 topics        Upload area resets        → ready
           and generated recs.

7000ms+     💬 [Ready for user input]               Ready for next upload     Main area
           [Input enabled]                                                    normal
```

---

## State Transitions

```
┌─────────────────┐
│  Idle           │
│ isAnalyzing:    │
│   false         │
│ events: []      │
└────────┬────────┘
         │
    User drops file
    startAnalysis()
         │
         ▼
┌─────────────────┐
│ Analyzing       │
│ isAnalyzing:    │
│   true          │
│ events: [recv]  │  ◄─── Events accumulate here
└────────┬────────┘       addEvent() called multiple times
         │
  completeAnalysis()
         │
         ▼
┌─────────────────┐
│  Complete       │
│ isAnalyzing:    │
│   false         │
│ (chat still     │
│  shows events)  │
└─────────────────┘
```

---

## Component Data Flow

```
CurriculumUpload.tsx          useUploadStore              ChatInterface.tsx
─────────────────────         ──────────────              ────────────────

User drops file
      ↓
handleDrop()
      ↓
handleAnalyze()
      ├─ startAnalysis()  ─────→ Store state changes
      │                          isAnalyzing = true
      │                          events = []
      │
      ├─ addEvent({type: '...'}) → Store updates
      │                            events = [{...}]
      │
      ├─ await api.upload()       ← Backend processes
      │
      ├─ addEvent({type: '...'})  ► Zustand notifies listeners
      │                            ↓
      │                        useEffect runs in ChatInterface
      │                        ↓
      │                        messages = [..., newMessage]
      │                        ↓
      │                        JSX re-renders
      │                        ↓
      │                        Chat bubble appears ✨
      │
      └─ completeAnalysis()
```

---

## Chat Message Rendering

```
For each event in the store:

event: {
  id: 'event-1712701234567',
  type: 'file_received',
  message: 'Received Math101.pdf! I\'m starting...',
  fileName: 'Math101.pdf',
  timestamp: 1712701234567,
  isAwaitingUserInput: false
}
      ↓
Convert to Message:
{
  id: 'event-1712701234567',
  role: 'assistant',  ← type='file_received' → assistant
  content: 'Received Math101.pdf!...',
  isAwaitingInput: false
}
      ↓
Render:
┌─────────────────────┐
│ 🤖 Received         │
│ Math101.pdf! I'm    │ ◄─ bg-gray-100
│ starting the deep   │   (assistant message)
│ analysis now. 🔍    │
└─────────────────────┘
      ↑
   Auto-scroll
   (+ smooth scroll)
```

---

## Event to Message Mapping

```
Event Type              Role          Styling           Display
─────────────────────   ─────────   ───────────────   ─────────────────
file_received           assistant   bg-gray-100       Normal message
confirming_topics       assistant   bg-gray-100       Normal message
confirmation_question   system      bg-yellow-50      ⚠️ Notification
                                    border-yellow    💬 Awaiting input
embedding               assistant   bg-gray-100       Normal message
complete                assistant   bg-gray-100       ✓ Success
error                   assistant   bg-red-50         ❌ Error
```

---

## Performance Timeline

```
Milliseconds       What's Happening
────────────────────────────────────────────────────
0 ms              startAnalysis() called
                  addEvent('file_received')

0-100 ms          React re-render in ChatInterface
                  New message added to DOM
                  Auto-scroll trigger

1500 ms           Delay complete
                  addEvent('confirming_topics')
                  React re-render + scroll

1500-2000 ms      API request in progress
                  Backend:
                  - Parsing file
                  - Extracting topics with Gemini
                  - Generating embeddings

2000 ms           API response received
                  addEvent('confirmation_question')
                  Zustand notify listeners

2000-2100 ms      React updates chat
                  Yellow system message appears
                  Input still disabled

4000 ms           Auto-confirm (simulates user saying "yes")
                  addEvent('confirmation_question' with response)
                  Message updated

5000 ms           BERT embedding phase begins
                  addEvent('embedding')
                  Main content area blurs

5000-6500 ms      "Processing..." animation runs
                  User attention on chat sidebar

6500 ms           completeAnalysis() called
                  setAnalyzing = false
                  Input enabled
                  addEvent('complete')

6500-7000 ms      Final success message displayed
                  User can interact again

Total Time: ~7 seconds for complete flow
Good UX: Feels fast due to interactive feedback
```

---

## Accessibility Features

The current implementation includes:

✅ **Semantic HTML**
- Proper button types and form submission
- Input disabled state managed

✅ **Visual Feedback**
- Message bubbles with distinct colors
- Loading animation (3 bouncing dots)
- Status messages in header (🔄 Analyzing)

✅ **Keyboard Navigation**
- Input field accepts focus
- Button click + Enter key submit
- Tab through controls

✅ **Screen Reader Support** (recommended additions)
- Add `aria-live="polite"` to chat messages
- Add `aria-label` to buttons
- Add `role="status"` to processing messages

---

## Testing Scenarios

### Happy Path
```
1. Drag Math101.pdf
   ✅ Chat shows "Received"
   ✅ File ready to analyze
   
2. Wait 1.5s
   ✅ Chat shows topic confirmation
   
3. Wait 2s
   ✅ Chat auto-confirms
   
4. Wait 1s
   ✅ Chat shows "Running BERT"
   ✅ Main area blurs
   
5. Wait 1.5s
   ✅ Chat shows complete
   ✅ Main area returns
   ✅ Input enabled
```

### Error Handling
```
1. Upload returns error
   ✅ completeAnalysis() still called
   ✅ Error message displayed
   ✅ Input re-enabled
   ✅ User can try again
```

### Rapid Uploads
```
1. Upload file A
   ✅ Chat shows analysis
   
2. Upload file B (before A finishes)
   ✅ startAnalysis('B')
   ✅ Events cleared
   ✅ Only B's messages shown
```

