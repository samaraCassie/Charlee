import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Filter, Search, FileAudio, FileImage, Calendar, RefreshCw } from 'lucide-react';
import { attachmentsService, type Attachment } from '@/services/attachmentsService';
import { AttachmentsList } from '@/components/AttachmentsList';
import { LoadingState } from '@/components/LoadingState';
import { useToast } from '@/hooks/use-toast';

export default function TranscriptionHistory() {
  const { toast } = useToast();

  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [filteredAttachments, setFilteredAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [fileTypeFilter, setFileTypeFilter] = useState<'all' | 'audio' | 'image'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    audio: 0,
    image: 0,
  });

  useEffect(() => {
    fetchAttachments();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [attachments, fileTypeFilter, searchQuery]);

  const fetchAttachments = async () => {
    try {
      setLoading(true);
      const data = await attachmentsService.getAllAttachments({
        limit: 500,
      });

      setAttachments(data);

      // Calculate stats
      setStats({
        total: data.length,
        audio: data.filter((a) => a.file_type === 'audio').length,
        image: data.filter((a) => a.file_type === 'image').length,
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível carregar o histórico de transcrições.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshAttachments = async () => {
    setRefreshing(true);
    await fetchAttachments();
    setRefreshing(false);
    toast({
      title: 'Atualizado',
      description: 'Histórico de transcrições atualizado com sucesso.',
    });
  };

  const applyFilters = () => {
    let filtered = [...attachments];

    // File type filter
    if (fileTypeFilter !== 'all') {
      filtered = filtered.filter((a) => a.file_type === fileTypeFilter);
    }

    // Search filter (in file name and processed text)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (a) =>
          a.file_name.toLowerCase().includes(query) ||
          a.processed_text?.toLowerCase().includes(query)
      );
    }

    setFilteredAttachments(filtered);
  };

  const handleDownload = async (attachmentId: number) => {
    try {
      const attachment = attachments.find((a) => a.id === attachmentId);
      await attachmentsService.downloadAttachment(
        attachmentId,
        attachment?.file_name
      );
      toast({
        title: 'Download iniciado',
        description: 'O arquivo está sendo baixado.',
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível baixar o anexo.',
        variant: 'destructive',
      });
    }
  };

  const handleReprocess = async (attachmentId: number) => {
    try {
      const updated = await attachmentsService.reprocessAttachment(attachmentId);
      setAttachments((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
      toast({
        title: 'Reprocessamento concluído',
        description: 'O anexo foi reprocessado com sucesso.',
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível reprocessar o anexo.',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (attachmentId: number) => {
    try {
      await attachmentsService.deleteAttachment(attachmentId);
      setAttachments((prev) => prev.filter((a) => a.id !== attachmentId));
      toast({
        title: 'Anexo excluído',
        description: 'O anexo foi removido com sucesso.',
      });

      // Update stats
      const deletedAttachment = attachments.find((a) => a.id === attachmentId);
      if (deletedAttachment) {
        setStats((prev) => ({
          total: prev.total - 1,
          audio:
            deletedAttachment.file_type === 'audio' ? prev.audio - 1 : prev.audio,
          image:
            deletedAttachment.file_type === 'image' ? prev.image - 1 : prev.image,
        }));
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível excluir o anexo.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-4xl font-bold tracking-tight">
            Histórico de Transcrições
          </h1>
          <p className="text-muted-foreground mt-1 md:mt-2 text-sm md:text-base">
            Visualize e gerencie todas as suas transcrições e análises de imagem.
          </p>
        </div>
        <Button onClick={refreshAttachments} disabled={refreshing}>
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <h3 className="text-2xl font-bold">{stats.total}</h3>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                <Calendar className="h-6 w-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Áudios</p>
                <h3 className="text-2xl font-bold">{stats.audio}</h3>
              </div>
              <div className="h-12 w-12 rounded-full bg-purple-500/10 flex items-center justify-center">
                <FileAudio className="h-6 w-6 text-purple-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Imagens</p>
                <h3 className="text-2xl font-bold">{stats.image}</h3>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <FileImage className="h-6 w-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Tipo</label>
              <Select
                value={fileTypeFilter}
                onValueChange={(value: 'all' | 'audio' | 'image') =>
                  setFileTypeFilter(value)
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="audio">Áudios</SelectItem>
                  <SelectItem value="image">Imagens</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Buscar</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Nome do arquivo ou texto..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Attachments List */}
      {loading ? (
        <LoadingState message="Carregando histórico..." variant="card" />
      ) : filteredAttachments.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileAudio className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-lg font-medium mb-2">Nenhum anexo encontrado</h3>
            <p className="text-sm text-muted-foreground">
              {searchQuery || fileTypeFilter !== 'all'
                ? 'Tente ajustar os filtros de busca.'
                : 'Comece criando tarefas com áudio ou imagens.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div>
          <div className="mb-4">
            <p className="text-sm text-muted-foreground">
              {filteredAttachments.length === attachments.length
                ? `Mostrando todos os ${filteredAttachments.length} anexos`
                : `Mostrando ${filteredAttachments.length} de ${attachments.length} anexos`}
            </p>
          </div>

          <AttachmentsList
            attachments={filteredAttachments}
            onDownload={handleDownload}
            onReprocess={handleReprocess}
            onDelete={handleDelete}
          />
        </div>
      )}
    </div>
  );
}
