document.addEventListener('DOMContentLoaded', function() {

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

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Change default behavior of submit button and add new event listener to it to run send_mail function
  document.querySelector('#compose-form').addEventListener('submit', function (event) { 
                                                            event.preventDefault(); 
                                                            const promise = send_mail();     
                                                            promise.then(() => load_mailbox('sent'));
                                                          }); // Load sent page

}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  // Get emails
  let promise = get_emails(mailbox);
  promise.then((data) => create_mail_list(data));
}

// Send mail
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
    console.log(result);

  }
  catch (error) {
    console.error(error);
  }
}

// Get emails from mailbox  
async function get_emails(mailbox) {

  // Make GET request to server
  try {
    const response = await fetch(`http://127.0.0.1:8000/emails/${mailbox}`);

    const result = await response.json();
    console.log(result);
    return result;

  }
  catch (error) {
    console.error(error);
  }
}

// Add mails to DOM - Create mail list
function create_mail_list(json_response) {

  let mails_view = document.querySelector('#emails-view');
  mails_view.classList.add('list-group', 'list-group-flush');

  for (const mail of json_response) {
    // Create mail row
    let mail_item = document.createElement('a');
    // TODO Change it to detail mail
    mail_item.href = "#";
    mail_item.classList.add('list-group-item', 'list-group-item-action');
    // If mail is read - gray background
    if (mail_item.read) {
      mail_item.classList.add('list-group-item-dark');
    }
    mail_item.innerHTML = `From ${mail.sender}: ${mail.subject}. At ${mail.timestamp}`;
    mails_view.appendChild(mail_item);
  };
};