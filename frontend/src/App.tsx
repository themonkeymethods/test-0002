import { useMemo, useState } from "react";
import "./index.css";

type Account = {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
};

type Membership = {
  accountId: number;
  role: "admin" | "member";
};

type User = {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
  isSuperuser: boolean;
  memberships: Membership[];
};

const accounts: Account[] = [
  { id: 1, name: "Acme Corp", email: "billing@acme.test", isActive: true },
  {
    id: 2,
    name: "Northwind Traders",
    email: "finance@northwind.test",
    isActive: true,
  },
  { id: 3, name: "Globex", email: "ops@globex.test", isActive: false },
];

const users: User[] = [
  {
    id: 1,
    name: "Super User",
    email: "superuser@test.com",
    isActive: true,
    isSuperuser: true,
    memberships: [
      { accountId: 1, role: "admin" },
      { accountId: 2, role: "admin" },
    ],
  },
  {
    id: 2,
    name: "Alex Admin",
    email: "admin@acme.test",
    isActive: true,
    isSuperuser: false,
    memberships: [{ accountId: 1, role: "admin" }],
  },
  {
    id: 3,
    name: "Casey Editor",
    email: "editor@northwind.test",
    isActive: true,
    isSuperuser: false,
    memberships: [
      { accountId: 1, role: "member" },
      { accountId: 2, role: "admin" },
    ],
  },
];

const App = () => {
  const [currentUserId, setCurrentUserId] = useState(1);
  const [activeAccountId, setActiveAccountId] = useState<number | null>(1);
  const currentUser = useMemo(
    () => users.find((user) => user.id === currentUserId) ?? users[0],
    [currentUserId]
  );

  const availableAccounts = useMemo(() => {
    if (currentUser.isSuperuser) {
      return accounts;
    }
    const allowed = new Set(currentUser.memberships.map((m) => m.accountId));
    return accounts.filter((account) => allowed.has(account.id));
  }, [currentUser]);

  const activeAccount = useMemo(
    () => accounts.find((account) => account.id === activeAccountId) ?? null,
    [activeAccountId]
  );

  return (
    <main className="app">
      <header className="page-header">
        <div>
          <p className="eyebrow">Admin Console</p>
          <h1>Account & User Management</h1>
          <p className="subtitle">
            Manage logins, roles, and account access in one place.
          </p>
        </div>
        <div className="user-switch">
          <label htmlFor="user-select">Signed in as</label>
          <select
            id="user-select"
            value={currentUserId}
            onChange={(event) => {
              const nextId = Number(event.target.value);
              setCurrentUserId(nextId);
              const nextUser = users.find((user) => user.id === nextId);
              if (nextUser?.isSuperuser) {
                setActiveAccountId(accounts[0]?.id ?? null);
              } else {
                setActiveAccountId(nextUser?.memberships[0]?.accountId ?? null);
              }
            }}
          >
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Active session</h2>
            <p className="muted">
              Role-based access checks determine which admin actions are available.
            </p>
          </div>
          <div className="status-tags">
            {currentUser.isSuperuser && <span className="tag">Superuser</span>}
            {currentUser.isActive ? (
              <span className="tag tag-success">Active</span>
            ) : (
              <span className="tag tag-warning">Inactive</span>
            )}
          </div>
        </div>
        <div className="session-grid">
          <div>
            <p className="label">User</p>
            <p className="value">{currentUser.name}</p>
            <p className="muted">{currentUser.email}</p>
          </div>
          <div>
            <p className="label">Role assignments</p>
            <div className="chips">
              {currentUser.memberships.map((membership) => {
                const accountName =
                  accounts.find((account) => account.id === membership.accountId)
                    ?.name ?? "Unknown";
                return (
                  <span className="chip" key={`${membership.accountId}-${membership.role}`}>
                    {accountName}: {membership.role}
                  </span>
                );
              })}
            </div>
          </div>
          <div>
            <p className="label">Active account</p>
            <p className="value">
              {activeAccount ? activeAccount.name : "No account selected"}
            </p>
            <p className="muted">
              {activeAccount ? activeAccount.email : "Switch accounts to manage data"}
            </p>
          </div>
        </div>
        {currentUser.isSuperuser && (
          <div className="switch-card">
            <div>
              <h3>Superuser account switch</h3>
              <p className="muted">
                Move between customer accounts to troubleshoot, audit, or delegate access.
              </p>
            </div>
            <div className="switch-controls">
              <label htmlFor="account-select">Acting on behalf of</label>
              <select
                id="account-select"
                value={activeAccountId ?? ""}
                onChange={(event) => {
                  const nextValue = event.target.value;
                  setActiveAccountId(nextValue ? Number(nextValue) : null);
                }}
              >
                <option value="">No account selected</option>
                {availableAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name}
                  </option>
                ))}
              </select>
              <button type="button" className="primary">
                Switch account
              </button>
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Accounts</h2>
            <p className="muted">Review status and contact information.</p>
          </div>
          <button type="button">Add account</button>
        </div>
        <div className="table">
          <div className="table-header">
            <span>Name</span>
            <span>Email</span>
            <span>Status</span>
            <span>Actions</span>
          </div>
          {accounts.map((account) => (
            <div className="table-row" key={account.id}>
              <span>{account.name}</span>
              <span>{account.email}</span>
              <span>
                {account.isActive ? (
                  <span className="tag tag-success">Active</span>
                ) : (
                  <span className="tag tag-warning">Inactive</span>
                )}
              </span>
              <span className="row-actions">
                <button type="button">View</button>
                <button type="button">Edit</button>
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Users</h2>
            <p className="muted">Manage membership roles and access.</p>
          </div>
          <button type="button">Invite user</button>
        </div>
        <div className="table">
          <div className="table-header">
            <span>User</span>
            <span>Accounts</span>
            <span>Status</span>
            <span>Actions</span>
          </div>
          {users.map((user) => (
            <div className="table-row" key={user.id}>
              <span>
                <strong>{user.name}</strong>
                <span className="muted">{user.email}</span>
              </span>
              <span className="chips">
                {user.memberships.map((membership) => {
                  const accountName =
                    accounts.find((account) => account.id === membership.accountId)
                      ?.name ?? "Unknown";
                  return (
                    <span className="chip" key={`${user.id}-${membership.accountId}`}>
                      {accountName}: {membership.role}
                    </span>
                  );
                })}
              </span>
              <span>
                {user.isActive ? (
                  <span className="tag tag-success">Active</span>
                ) : (
                  <span className="tag tag-warning">Inactive</span>
                )}
                {user.isSuperuser && <span className="tag">Superuser</span>}
              </span>
              <span className="row-actions">
                <button type="button">Reset password</button>
                <button type="button">Disable</button>
              </span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
};

export default App;
