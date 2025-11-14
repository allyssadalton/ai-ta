<script lang="ts">
  import { onMount } from "svelte";

  let courses = [
    "CSCI155 - Intro to Programming",
    "CSCI230 - Comp Arch & Parallel Computing",
    "CSCI240 - Data Structures and Algorithms",
    "CSCI340 - Computer Algorithms",
    "CSCI370 - Database Systems",
    "CSCI420 - Networks & Distrib Computing",
    "CSCI421 - Data Encrypt/Network Security"
  ];

  let selectedCourse = courses[0];
  let question = "";
  let chatHistory: { sender: string; text: string }[] = [];

  //  update this URL to match your backend
  const BACKEND_URL = "https://ai-ta-backend-249857968225.us-south1.run.app";

  async function askQuestion() {
    if (!question.trim()) return;

    // Add user message
    chatHistory = [...chatHistory, { sender: "user", text: question }];
    const currentQuestion = question;
    question = "";

    try {
      const res = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: currentQuestion,
          course: selectedCourse
        })
      });

      const data = await res.json();

      chatHistory = [
        ...chatHistory,
        { sender: "ai", text: data.answer || "No answer received." }
      ];
    } catch (err) {
      console.error(err);
      chatHistory = [
        ...chatHistory,
        { sender: "ai", text: "Error contacting backend. Please notify your instructor." }
      ];
    }
  }

</script>

<!-- Layout -->
<div class="flex h-screen bg-gray-50 text-gray-800">
  <!-- Sidebar -->
  <aside
    class="w-[25vw] border-r border-gray-200 bg-[#A9A8A9] flex flex-col h-screen p-0 m-0"
  >
    <div class="flex items-center gap-2 border-b border-gray-100" style="margin-left: 3px;">
      <img src="/uindylogo.png" alt="Logo" class="w-[12vh]" />
    </div>

    <nav class="flex-1 overflow-y-auto">
      <ul class="p-[1vw] mr-[0vw] ml-[0vw] list-none">
        <li>
          <input
            type="text"
            placeholder="Search Courses"
            class="w-full rounded-full border border-gray-300 bg-white focus:outline-none focus:ring-gray-400 text-[18px] block" style="margin-top: 2; margin-bottom: 8px;"
          />
        </li>

        <li class="text-[24px] font-[Arial] font-[700]" style="margin-top: 12px; margin-bottom: 20px;">
          Courses
        </li>

        {#each courses as course}
          <li class="m-0 p-0">
            <button
              class="w-full text-left pl-0 pr-3 py-2 rounded-md hover:bg-gray-100 border-none text-[18px] text-white
                {selectedCourse === course ? 'selected' : ''}"
              on:click={() => (selectedCourse = course)} style="padding-top: 15px; padding-bottom: 15px; background: #B20A38;"
            > 
              <span class="block">{course}</span>
            </button>
          </li>
        {/each}
      </ul>
    </nav>
  </aside>

  <!-- Chat Area -->
  <main class="flex-1 flex flex-col">
    <!-- Header -->
    <header
      class="flex items-center justify-between border-b border-gray-200 bg-[#A9A8A9] text-[#B20A38] font-[Arial] px-4 py-2"
    >
      <h1 class="font-semibold text-lg" style="margin-left: 8px;">Ask Allyssa</h1>
      <span class="italic text-sm text-gray-700" style="margin-right: 8px;">{selectedCourse}</span>
    </header>

    <!-- Chat Messages -->
    <!-- <div
      class="flex-1 overflow-y-auto p-6 flex flex-col space-y-4 bg-gray-50"
      id="chat-window"
    >
      {#each chatHistory as msg, i}
        <div
          class="max-w-[70%] px-4 py-3 rounded-3xl shadow-sm transition-all duration-300"
          class:bg-gray-200={msg.sender === 'user'}
          class:bg-[#A9A8A9]={msg.sender === 'ai'}
          class:self-end={msg.sender === 'user'}
          class:self-start={msg.sender === 'ai'}
        >
          <p class="text-[16px] leading-snug whitespace-pre-wrap">{msg.text}</p>
        </div>
      {/each}
    </div> -->
<div
  id="chat-window"
  class="flex-1 overflow-y-auto bg-gray-50 py-6 px-4 flex flex-col space-y-4"
>
  {#each chatHistory as msg, i}
    <div
      class="flex w-full"
      class:justify-end={msg.sender === 'user'}
      class:justify-start={msg.sender === 'ai'}
    >
      <div
        class="max-w-[70%] px-4 py-3 rounded-2xl shadow-sm transition-all duration-300 text-[16px] leading-snug whitespace-pre-wrap"  style="border-radius: .5rem; padding-left: 4px; padding-right: 4px; padding-top: 3px; padding-bottom: 3px; margin-top: 8px; margin-top: 8px; margin-left: 4px; margin-right: 4px;"
        class:bg-[#4ca3e0]={msg.sender === 'user'}
        class:text-[#f5f5f5]={msg.sender === 'user'}
        class:bg-[#7d7d7d]={msg.sender === 'ai'}
        class:text-[#f5f2f2]={msg.sender === 'ai'}
      >
        {msg.text}
      </div>
    </div>
  {/each}
</div>


    <!-- Input box -->
    <footer class="p-4 border-t border-gray-200 bg-white">
      <div class="flex items-center gap-2">
        <input
          type="text"
          bind:value={question}
          placeholder={`Ask anything about ${selectedCourse}`}
          class="flex-1 px-4 py-2 text-[18px] border rounded-full focus:outline-none focus:ring-gray-300"
          on:keydown={(e) => e.key === 'Enter' && askQuestion()}
        />
        <button
          class="px-4 py-2 bg-gray-800 text-white rounded-full hover:bg-gray-400 text-[18px]"
          on:click={askQuestion}
        >
          Send
        </button>
      </div>
    </footer>
  </main>
</div>

<style>
  .selected {
    background-color: #f3f4f6;
    font-weight: 600;
  }


  #chat-window {
    scrollbar-width: thin;
    scrollbar-color: #9ca3af #e5e7eb; /* thumb gray-400, track gray-200 */
  }

  #chat-window::-webkit-scrollbar {
    width: 8px;
  }

  #chat-window::-webkit-scrollbar-track {
    background: #e5e7eb;
  }

  #chat-window::-webkit-scrollbar-thumb {
    background-color: #9ca3af;
    border-radius: 4px;
  }

	
</style>
