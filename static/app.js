let currentConversationId = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await loadConversations();
        await loadDocuments();
        setupChatForm();
        setupNewConversation();
        setupUploadForm();

        document.getElementById(
            "refreshDocumentsBtn"
        ).addEventListener(
            "click",
            loadDocuments
        );

    }
);


async function loadConversations() {

    const response = await fetch(
        "/conversations"
    );

    if (!response.ok) {
        console.error(
            "Unable to load conversations"
        );
        return;
    }

    const conversations =
        await response.json();

    const list =
        document.getElementById(
            "conversationList"
        );

    list.innerHTML = "";

    conversations.forEach(
        conversation => {

            const item =
                document.createElement("div");

            item.className =
                "conversation-item";

            item.textContent =
                conversation.title ||
                "Untitled Conversation";

            item.dataset.id =
                conversation.id;

            item.addEventListener(
                "click",
                () => {
                    loadConversation(
                        conversation.id
                    );
                }
            );

            list.appendChild(item);
        }
    );
}


async function loadConversation(
    conversationId
) {

    const response = await fetch(
        `/conversations/${conversationId}`
    );

    if (!response.ok) {
        return;
    }

    const data =
        await response.json();

    currentConversationId =
        conversationId;

    document.getElementById(
        "conversationTitle"
    ).textContent =
        data.conversation.title ||
        "Conversation";

    const container =
        document.getElementById(
            "chatMessages"
        );

    container.innerHTML = "";

    data.messages.forEach(
        message => {

            addMessage(
                message.role,
                message.content,
                message.sources || []
            );

        }
    );

    highlightConversation(
        conversationId
    );
}


function setupNewConversation() {

    document.getElementById(
        "newConversationBtn"
    ).addEventListener(
        "click",
        () => {

            currentConversationId = null;

            document.getElementById(
                "conversationTitle"
            ).textContent =
                "New Conversation";

            document.getElementById(
                "chatMessages"
            ).innerHTML = `
                <div
                    id="emptyState"
                    class="text-center text-muted mt-5"
                >
                    <h4>Ask a question</h4>
                    <p>
                        Answers will be generated
                        using your uploaded documents.
                    </p>
                </div>
            `;

            highlightConversation(null);
        }
    );
}


function setupChatForm() {

    const form =
        document.getElementById(
            "chatForm"
        );

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const input =
                document.getElementById(
                    "questionInput"
                );

            const question =
                input.value.trim();

            if (!question) {
                return;
            }

            removeEmptyState();

            addMessage(
                "user",
                question
            );

            input.value = "";

            setLoading(true);
            console.log("Sending conversation ID: ", currentConversationId);
            try {
                const response =
                    await fetch(
                        "/chat",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },
                            
                            body: JSON.stringify({
                                question:
                                    question,

                                conversation_id:
                                    currentConversationId,

                                top_k: 2
                            })
                        }
                    );

                const data =
                    await response.json();
                
                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Chat request failed"
                    );
                }

                currentConversationId =
                    data.conversation_id;

                addMessage(
                    "assistant",
                    data.answer,
                    data.sources
                );

                await loadConversations();

                highlightConversation(
                    currentConversationId
                );

            }
            catch (error) {

                addMessage(
                    "assistant",
                    "Error: " +
                    error.message
                );

            }
            finally {

                setLoading(false);

            }

        }
    );
}


function addMessage(
    role,
    content,
    sources = []
) {

    const container =
        document.getElementById(
            "chatMessages"
        );

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        role === "user"
            ? "message message-user"
            : "message message-assistant";

    const text =
        document.createElement("div");

    text.textContent =
        content;

    wrapper.appendChild(text);


    if (
        role === "assistant" &&
        sources &&
        sources.length > 0
    ) {

        const sourceContainer =
            document.createElement(
                "div"
            );

        sourceContainer.className =
            "sources";

        const title =
            document.createElement(
                "strong"
            );

        title.textContent =
            "Sources";

        sourceContainer.appendChild(
            title
        );


        sources.forEach(
            source => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "source-item";

                item.textContent =
                    `${source.filename} | chunk ${source.chunk_index}`;

                sourceContainer.appendChild(
                    item
                );

            }
        );

        wrapper.appendChild(
            sourceContainer
        );
    }


    container.appendChild(
        wrapper
    );

    container.scrollTop =
        container.scrollHeight;
}


function removeEmptyState() {

    const emptyState =
        document.getElementById(
            "emptyState"
        );

    if (emptyState) {
        emptyState.remove();
    }
}


function setLoading(
    loading
) {

    const loadingState =
        document.getElementById(
            "loadingState"
        );

    const sendButton =
        document.getElementById(
            "sendButton"
        );

    if (loading) {

        loadingState.classList.remove(
            "d-none"
        );

        sendButton.disabled =
            true;

    }
    else {

        loadingState.classList.add(
            "d-none"
        );

        sendButton.disabled =
            false;
    }
}


function highlightConversation(
    conversationId
) {

    document
        .querySelectorAll(
            ".conversation-item"
        )
        .forEach(
            item => {

                item.classList.toggle(
                    "active",
                    item.dataset.id ===
                    conversationId
                );

            }
        );
}


function setupUploadForm() {

    const form =
        document.getElementById(
            "uploadForm"
        );

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const fileInput =
                document.getElementById(
                    "documentFile"
                );

            const status =
                document.getElementById(
                    "uploadStatus"
                );

            const uploadButton =
                document.getElementById(
                    "uploadButton"
                );

            if (
                !fileInput.files.length
            ) {
                return;
            }

            const formData =
                new FormData();

            formData.append(
                "file",
                fileInput.files[0]
            );

            uploadButton.disabled =
                true;

            status.innerHTML =
                `
                <div class="text-muted">
                    Uploading and indexing...
                </div>
                `;

            try {

                const response =
                    await fetch(
                        "/documents/upload",
                        {
                            method:
                                "POST",

                            body:
                                formData
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Upload failed"
                    );
                }

                status.innerHTML =
                    `
                    <div class="alert alert-success">
                        ${data.filename}
                        indexed successfully.
                        ${data.chunks}
                        chunks created.
                    </div>
                    `;

                fileInput.value = "";
                await loadDocuments();

            }
            catch (error) {

                status.innerHTML =
                    `
                    <div class="alert alert-danger">
                        ${error.message}
                    </div>
                    `;

            }
            finally {

                uploadButton.disabled =
                    false;

            }

        }
    );
}

async function loadDocuments() {

    const response =
        await fetch("/documents");

    if (!response.ok) {
        return;
    }

    const documents =
        await response.json();
    console.log("Documents returned:", documents);
    const container =
        document.getElementById(
            "documentList"
        );

    container.innerHTML = "";

    documents.forEach(
        doc => {

            const wrapper =
                document.createElement("div");

            wrapper.className =
                "border rounded p-2 mb-2";

            wrapper.innerHTML = `
                <div>
                    <strong>
                        ${doc.original_filename}
                    </strong>
                </div>

                <div class="text-muted">
                    ${doc.status}
                    |
                    ${doc.chunk_count} chunks
                </div>

                <button
                    class="btn btn-sm btn-outline-primary mt-2"
                    onclick="reindexDocument('${doc.id}')"
                >
                    Re-index
                </button>

                <button
                    class="btn btn-sm btn-outline-danger mt-2"
                    onclick="deleteDocument('${doc.id}')"
                >
                    Delete
                </button>
            `;

            container.appendChild(
                wrapper
            );
        }
    );
}

async function deleteDocument(
    documentId
) {

    if (
        !confirm(
            "Delete this document?"
        )
    ) {
        return;
    }

    const response =
        await fetch(
            `/documents/${documentId}`,
            {
                method: "DELETE"
            }
        );

    if (!response.ok) {
        alert(
            "Failed to delete document"
        );
        return;
    }

    await loadDocuments();
}

async function reindexDocument(
    documentId
) {

    const response =
        await fetch(
            `/documents/${documentId}/reindex`,
            {
                method: "POST"
            }
        );

    if (!response.ok) {

        const data =
            await response.json();

        alert(
            data.detail ||
            "Re-index failed"
        );

        return;
    }

    await loadDocuments();
}