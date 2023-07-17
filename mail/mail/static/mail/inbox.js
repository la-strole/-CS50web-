// Create email view

const email_card = document.createElement('div');
email_card.classList.add('card');
email_card.setAttribute('id', 'email-view');
const card_body = document.createElement('div');
card_body.classList.add('card-body');
const card_title = document.createElement('h5');
card_title.classList.add('card-title');
const card_sender = document.createElement('h6');
card_sender.classList.add('card-subtitle', 'mb-2', 'text-muted');
const card_recipients = document.createElement('h6');
card_recipients.classList.add('card-subtitle', 'mb-2', 'text-muted');
const card_timestamp = document.createElement('h6');
card_timestamp.classList.add('card-subtitle', 'mb-2', 'text-muted');
const card_text = document.createElement('p');
card_text.classList.add('card-text');
const card_archive_button = document.createElement('a');
card_archive_button.classList.add('btn', 'btn-primary');
card_archive_button.href = '#';
email_card.appendChild(card_body);
card_body.appendChild(card_title);
card_body.appendChild(card_sender);
card_body.appendChild(card_recipients);
card_body.appendChild(card_timestamp);
card_body.appendChild(card_text);
card_body.appendChild(card_archive_button);


document.addEventListener('DOMContentLoaded', function() {

  // Add new view (email view) to the DOM
  const emails_view = document.querySelector('#emails-view');
  emails_view.after(email_card);

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Change default behavior of submit button and add new event listener to it to run send_mail function
  document.querySelector('#compose-form').addEventListener('submit', function (event) { 
                                                            event.preventDefault(); 
                                                            const promise = send_mail();     
                                                            promise.then(() => load_mailbox('sent')); // Load sent page
                                                          }); 
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  // Get emails
  const promise = get_emails(mailbox);
  promise.then((data) => {
    console.log(data);
    // Create email list in DOM
    let mails_view = document.querySelector('#emails-view');
    mails_view.classList.add('list-group', 'list-group-flush');
    for (const mail of data) {
      // Create mail row
      let mail_item = document.createElement('a');
      // To detail mail
      mail_item.href = `javascript:load_email(${mail.id}, '${mailbox}');`;
      mail_item.classList.add('list-group-item', 'list-group-item-action');
      // If mail is read - gray background
      if (mail.read) {
        mail_item.classList.add('list-group-item-dark');
      }
      mail_item.innerHTML = `From ${mail.sender}: ${mail.subject}. At ${mail.timestamp}`;
      mails_view.appendChild(mail_item);
    };
  });
}

function load_email(mail_id, mailbox) {
  // Get mail from server
  const response = get_mail(mail_id);
  response.then((email_object) => {
    // Show email view 
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'block';

    card_title.innerHTML = `Subject: ${email_object.subject}`;
    card_sender.innerHTML = `From: ${email_object.sender}`;
    card_recipients.innerHTML = 'To: ' + (email_object.recipients).join(",\n");
    card_timestamp.innerHTML = (email_object.timestamp);
    card_text.innerHTML = (email_object.body);
    if (mailbox != 'sent') {
      card_archive_button.style.visibility = 'visible';
      if (email_object.archived) {
        card_archive_button.innerHTML = 'Unarchive';
        card_archive_button.href = `javascript:change_archive(${mail_id}, ${true})`;
      }
      else {
        card_archive_button.innerHTML = 'Archive';
        card_archive_button.href = `javascript:change_archive(${mail_id}, ${false})`;
      }
    }
    else {
      card_archive_button.style.visibility = 'hidden';
    }
  });
  // Make email read
  make_read(mail_id);
}

/* API manipulation */

// Send mail API
async function send_mail() {
  
  // Get values from form
  let body = {
    recipients: document.querySelector('#compose-recipients').value,
    subject: document.querySelector('#compose-subject').value,
    body: document.querySelector('#compose-body').value
  };

  // Make POST request to server to send mail
  try {
    const response = await fetch('http://127.0.0.1:8000/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    const result = await response.json();

  }
  catch (error) {
    console.error(error);
  }
}

// Get emails from mailbox API
async function get_emails(mailbox) {

  // Make GET request to server
  try {
    const response = await fetch(`http://127.0.0.1:8000/emails/${mailbox}`);

    const result = await response.json();
    return result;

  }
  catch (error) {
    console.error(error);
  }
}

// View email details API
async function get_mail(mail_id){
  try {
    const response = await fetch(`http://127.0.0.1:8000/emails/${mail_id}`);
    const result = await response.json();
    return result;
  }
  catch (error) {
    console.error(error);
  }
}

// Mark email as read API
async function make_read(mail_id){
  try {
    const response = await fetch(`http://127.0.0.1:8000/emails/${mail_id}`,
                                {
                                  method: 'PUT',
                                  headers: {
                                    'Content-Type': 'application/json'
                                  },
                                  body: JSON.stringify({
                                    read: true
                                  })
                                });
  }
  catch(error) {
    console.error(error);
  }
}

// Change Archive tag API
async function change_archive(mail_id, is_archived){
  try {
    const response = await fetch(`http://127.0.0.1:8000/emails/${mail_id}`,
                                {
                                  method: 'PUT',
                                  headers: {
                                    'Content-Type': 'application/json'
                                  },
                                  body: JSON.stringify({
                                    archived: !is_archived
                                  })
                                });
    // Load inbox
    load_mailbox('inbox');
  }
  catch(error) {
    console.error(error);
  }
}