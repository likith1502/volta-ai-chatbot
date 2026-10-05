import pytest
from app.integrations.adapters.storage.s3_adapter import S3StorageAdapter
from app.integrations.adapters.storage.azure_blob_adapter import AzureBlobStorageAdapter
from app.integrations.adapters.storage.gcs_adapter import GCSStorageAdapter
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter, FilesystemSandboxAdapter
from app.integrations.adapters.vector.qdrant_adapter import QdrantVectorAdapter
from app.integrations.adapters.vector.pinecone_adapter import PineconeVectorAdapter
from app.integrations.adapters.vector.faiss_adapter import FAISSVectorAdapter
from app.integrations.adapters.vector.chroma_adapter import ChromaVectorAdapter
from app.integrations.adapters.vector.vector_adapter import InMemoryVectorAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_storage_adapter_provider_ids_and_defaults():
    s3 = S3StorageAdapter()
    azure = AzureBlobStorageAdapter()
    gcs = GCSStorageAdapter()
    fs = FilesystemStorageAdapter()
    sandbox = FilesystemSandboxAdapter()

    assert s3.provider_id == "storage.s3"
    assert azure.provider_id == "storage.azure_blob"
    assert gcs.provider_id == "storage.gcs"
    assert fs.provider_id == "storage.filesystem"
    assert sandbox.provider_id == "storage.filesystem_sandbox"


@pytest.mark.asyncio
async def test_storage_adapter_initialization_safety_and_health_without_credentials():
    ctx = IntegrationContext()

    s3 = S3StorageAdapter()
    await s3.initialize(ctx)
    report_s3 = await s3.check_health()
    assert report_s3.provider_id == "storage.s3"
    assert report_s3.is_healthy is False
    assert report_s3.health_level in [HealthLevel.RED, HealthLevel.ORANGE]

    azure = AzureBlobStorageAdapter()
    await azure.initialize(ctx)
    report_azure = await azure.check_health()
    assert report_azure.provider_id == "storage.azure_blob"
    assert report_azure.is_healthy is False

    gcs = GCSStorageAdapter()
    await gcs.initialize(ctx)
    report_gcs = await gcs.check_health()
    assert report_gcs.provider_id == "storage.gcs"
    assert report_gcs.is_healthy is False


@pytest.mark.asyncio
async def test_vector_adapter_provider_ids_and_defaults():
    qdrant = QdrantVectorAdapter()
    pinecone = PineconeVectorAdapter()
    faiss = FAISSVectorAdapter()
    chroma = ChromaVectorAdapter()
    inmem = InMemoryVectorAdapter()

    assert qdrant.provider_id == "vector.qdrant"
    assert pinecone.provider_id == "vector.pinecone"
    assert faiss.provider_id == "vector.faiss"
    assert chroma.provider_id == "vector.chroma"
    assert inmem.provider_id == "vector.inmemory"


@pytest.mark.asyncio
async def test_inmemory_and_faiss_vector_operations():
    inmem = InMemoryVectorAdapter()
    await inmem.initialize()
    await inmem.upsert_vector("v1", [0.1, 0.2, 0.3], {"tag": "test"})
    res = await inmem.query_vector([0.1, 0.2, 0.3], top_k=1)
    assert len(res) == 1
    assert res[0][0] == "v1"

    report = await inmem.check_health()
    assert report.is_healthy is True
    assert report.health_level == HealthLevel.GREEN


@pytest.mark.asyncio
async def test_resource_cleanup_disconnect():
    s3 = S3StorageAdapter()
    await s3.disconnect()
    assert s3.status == IntegrationStatus.DISCONNECTED

    qdrant = QdrantVectorAdapter()
    await qdrant.disconnect()
    assert qdrant.status == IntegrationStatus.DISCONNECTED
